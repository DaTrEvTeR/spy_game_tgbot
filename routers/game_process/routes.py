from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from routers.game_process.keyboards import my_role
from routers.game_process.services import pass_turn, question_turn, setup_game_state, start_vote
from routers.game_states import GameData, GameStates
from routers.helpers import get_str_players_list

router = Router(name="game_process")

router.message.filter(F.chat.type.in_({"group", "supergroup"}), GameStates.game)


@router.callback_query(F.data == "init_game")
async def init_game(callback: CallbackQuery, state: FSMContext) -> None:
    """Initializes the game by assigning spies and setting the turn order.

    This function is triggered when the "init_game" callback query is received.
    It sets the game state to active, assigns spies randomly, and determines the
    order in which players will take turns.

    Parameters
    ----------
    callback : CallbackQuery
        The callback query triggered when the game is initialized.
    state : FSMContext
        The current finite state machine context, used to manage game data.

    """
    game_data = await GameData.init(state=state)

    await setup_game_state(game_data)

    await callback.message.answer(
        f"Участники:\n{get_str_players_list(game_data.players)}\nШпионов среди них: {len(game_data.spies)}",
        reply_markup=my_role,
    )
    await question_turn(callback=callback, game_data=game_data)


@router.callback_query(F.data == "my_role")
async def check_role(callback: CallbackQuery, state: FSMContext) -> None:
    """Informs the player of their role (spy or regular player) when they check their role.

    This function is triggered when the "my_role" callback query is received. It checks
    if the player is a spy or a regular player and sends a response accordingly.

    Parameters
    ----------
    callback : CallbackQuery
        The callback query triggered when a player requests to see their role.
    state : FSMContext
        The current finite state machine context, used to manage game data.
    """
    game_data = await GameData.init(state=state)

    if callback.from_user in game_data.spies:
        await callback.answer(
            text=(
                "Вы шпион"
                "\nЗадавайте вопросы осторожно и внимательно читайте ответы игроков, вам нужно вычислить локацию"
                "\nКак только будете уверенны в ответе пропишите команду /guess"
            ),
            show_alert=True,
        )
    else:
        await callback.answer(
            text=(
                "Вы сотрудник"
                "\nЗадавайте вопросы осторожно и внимательно читайте ответы игроков, вам нужно определить кто шпион"
                "\nКак только будете уверенны в ответе пропишите команду /vote"
            ),
            show_alert=True,
        )


@router.callback_query(F.data == "finished")
async def finished_button(callback: CallbackQuery, state: FSMContext) -> None:
    """Handles the callback when a game turn is finished and proceeds to the next player's turn.

    This function checks whether the user who initiated the callback is the current player
    allowed to take a turn. If not, it shows an alert. If the user is the current player,
    the function advances the turn, toggling between question and answer turns, and notifies
    the next player accordingly.

    Parameters
    ----------
    callback : CallbackQuery
        The callback query triggered by the user.
    state : FSMContext
        The FSMContext storing the current game state.
    """
    game_data = await GameData.init(state=state)

    if callback.from_user != game_data.order_list[game_data.cur_order_user_index]:
        await callback.answer(text="Сейчас не ваш ход!", show_alert=True)
        return

    await pass_turn(callback, game_data)


@router.message(Command("vote"))
async def ready_to_vote(message: Message, state: FSMContext) -> None:
    game_data = await GameData.init(state=state)

    user = message.from_user
    if user not in game_data.order_list:
        await message.delete()
        return

    game_data.ready_to_vote.add(user)
    await message.delete()
    if len(game_data.ready_to_vote) > len(game_data.order_list) / 2:
        await start_vote(message)


@router.message(F.text[0] != "/")
async def check_if_message_from_cur_turn_user(message: Message, state: FSMContext) -> None:
    """Checks if the message is sent by the current player whose turn it is.

    If the message is from a player who is not supposed to speak at this moment, and the
    message does not start with '/', it will be deleted.

    Parameters
    ----------
    message : Message
        The message sent by a user in the chat.
    state : FSMContext
        The FSMContext storing the current game state.
    """
    game_data = await GameData.init(state=state)

    if message.from_user != game_data.order_list[game_data.cur_order_user_index]:
        await message.delete()
