from random import choice, shuffle

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, User

from core.settings import settings
from routers.game_process.keyboards import complete_msg, my_role
from routers.game_states import GameData, GameStates
from routers.helpers import get_player_username_or_firstname, get_str_players_list

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
    await game_data.state.set_state(GameStates.game)
    game_data.spies = set_spies(game_data)
    game_data.order_list = set_players_order(game_data)
    await game_data.save()
    await callback.message.answer(
        f"Участники:\n{get_str_players_list(game_data.players)}\nШпионов среди них: {len(game_data.spies)}",
        reply_markup=my_role,
    )
    await callback.message.answer(
        text=(
            f"{get_player_username_or_firstname(game_data.order_list[game_data.cur_order_user_index])} задает вопрос "
            f"{get_player_username_or_firstname(game_data.order_list[game_data.cur_order_user_index+1])}:"
        ),
        reply_markup=complete_msg,
    )


def set_players_order(game_data: GameData) -> list[User]:
    """Shuffles and returns the list of players to define the turn order.

    Parameters
    ----------
    game_data : GameData
        The current game data containing the list of players.

    Returns:
    -------
    list[User]
        A shuffled list of players representing the order in which they will take turns.
    """
    order: list[User] = list(game_data.players)
    shuffle(order)
    return order


def set_spies(game_data: GameData) -> set[User]:
    """Randomly selects spies from the list of players.

    The number of spies is determined by dividing the total number of players by the
    minimal player count setting.

    Parameters
    ----------
    game_data : GameData
        The current game data containing the list of players.

    Returns:
    -------
    set[User]
        A set of users who have been selected as spies.
    """
    count_of_spies: int = len(game_data.players) // settings.minimal_player_count
    players_list = list(game_data.players.copy())
    spies = set()
    for _ in range(count_of_spies):
        spy = choice(players_list)
        spies.add(spy)
        players_list.remove(spy)
    return spies


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
async def game_chat(callback: CallbackQuery, state: FSMContext) -> None:
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

    cur_user_index = game_data.next_turn()
    await game_data.save()
    if game_data.is_question:
        answerer = get_asnwerer(game_data)
        await callback.message.answer(
            text=f"{get_player_username_or_firstname(game_data.order_list[cur_user_index])} задает вопрос {answerer}:",
            reply_markup=complete_msg,
        )
        await callback.answer()
    else:
        await callback.message.answer(
            text=f"{get_player_username_or_firstname(game_data.order_list[cur_user_index])} отвечает:",
            reply_markup=complete_msg,
        )
        await callback.answer()


def get_asnwerer(game_data: GameData) -> str:
    """Retrieves the username or first name of the next player in the order list who will answer the question.

    If the current player is not the last one in the order list, the next player is selected.
    Otherwise, the first player in the list is chosen.

    Parameters
    ----------
    game_data : GameData
        The current game data containing the player order.

    Returns:
    -------
    str
        The username or first name of the player who will answer the question.
    """
    if game_data.cur_order_user_index != len(game_data.order_list) - 1:
        answerer = get_player_username_or_firstname(game_data.order_list[game_data.cur_order_user_index + 1])
    else:
        answerer = get_player_username_or_firstname(game_data.order_list[0])
    return answerer


@router.message()
async def check_if_message_from_cur_turn_user(message: Message, state: FSMContext) -> None:
    """Checks if the message is sent by the current player whose turn it is.

    If the message is from a player who is not supposed to speak at this moment, and the
    message does not start with '!', it will be deleted.

    Parameters
    ----------
    message : Message
        The message sent by a user in the chat.
    state : FSMContext
        The FSMContext storing the current game state.
    """
    game_data = await GameData.init(state=state)
    if message.from_user != game_data.order_list[game_data.cur_order_user_index] and not message.text.startswith("!"):
        await message.delete()
