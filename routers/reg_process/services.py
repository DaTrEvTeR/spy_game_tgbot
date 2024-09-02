import asyncio
from random import randint

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, Update, User

from core.config import bot, dp
from core.settings import settings
from routers.game_states import GameStates
from routers.helpers import get_player_username_or_firstname, get_players_set_from_state, is_players_enough
from routers.reg_process.keyboards import reg


async def check_null_state(message: Message, state: FSMContext) -> bool:
    """Checks the current game state and sends a message
    if the game is already in progress or registration has started.

    Parameters
    ----------
    message : Message
        The message from the user that the bot should respond to.
    state : FSMContext
        The current state of the FSM used to track the game's status.
    """
    cur_state = await state.get_state()

    if cur_state == GameStates.game.state:
        await message.answer("Игра уже идет!")
        return False

    if cur_state == GameStates.registration.state:
        await message.answer("Регистрация уже началась!")
        return False

    return True


async def start_registration(message: Message, state: FSMContext) -> Message:
    """Starts the registration process for the game and sets up the registration timer.

    Parameters
    ----------
    message : Message
        The bot message that informs about the start of the registration.
    state : FSMContext
        The current state of the FSM used to track the game's state and registered players.
    """
    await state.set_state(GameStates.registration)
    await state.update_data(players=set())

    return await message.answer(
        text=settings.start_registration_msg,
        reply_markup=reg,
    )


async def manage_registration_timer(state: FSMContext) -> bool:
    """Manages the registration timer for starting or canceling a game.

    This function initiates a timer for the registration period and handles the game start or cancellation
    based on the number of registered players once the timer expires.
    The timer can be canceled manually, in which case the game will start immediately.

    Parameters
    ----------
    reg_message : Message
        The bot message sent to the chat when the registration starts.
        This message is updated based on the game state.
    state : FSMContext
        The current game state used to track ongoing processes and data.
    """
    timer = asyncio.create_task(asyncio.sleep(settings.registration_time))
    await state.update_data(registration_task=timer)

    try:
        await timer
        return await is_players_enough(state=state)
    except asyncio.CancelledError:
        return True


async def start_game(reg_message: Message, state: FSMContext) -> None:
    """Starts the game if the required number of players is reached.

    Parameters
    ----------
    reg_message : Message
        The bot message that will be updated to indicate the start of the game.
    state : FSMContext
        The current state of the FSM used to track the game's state.
    """
    await reg_message.edit_text(text="Набрано нужное количество игроков. Игра начинается.", reply_markup=None)
    await state.set_state(GameStates.game)

    callback_query = CallbackQuery(
        id="manual",
        from_user=reg_message.from_user,
        chat_instance=str(reg_message.chat.id),
        message=reg_message,
        data="init_game",
    )

    update = Update(update_id=randint(1, 9999), callback_query=callback_query)

    await dp.feed_update(bot=bot, update=update)


async def game_cancel(reg_message: Message, state: FSMContext) -> None:
    """Cancels the game if the required number of players is not reached.

    Parameters
    ----------
    reg_message : Message
        The bot message that will be updated to indicate the cancellation of the registration.
    state : FSMContext
        The current state of the FSM used to clear the game's state.
    """
    await reg_message.edit_text(text="Недостаточно игроков. Регистрация отменена.", reply_markup=None)
    await state.clear()


async def start_game_now_logic(callback: CallbackQuery, state: FSMContext) -> None:
    """Handles the logic for starting the game immediately if players press the start now button.

    Parameters
    ----------
    callback : CallbackQuery
        The callback initiated by the user to start the game immediately.
    state : FSMContext
        The current state of the FSM used to check the number of players and cancel the registration timer.
    """
    if await is_players_enough(state):
        data = await state.get_data()
        registration_task = data.get("registration_task")
        registration_task.cancel()
    else:
        await callback.answer(
            f"Минимальное количество игроков для начала игры: {settings.minimal_player_count}", show_alert=True
        )


async def reg_button_logic(callback: CallbackQuery, state: FSMContext) -> None:
    """Handles the logic for the registration button to join or leave the game.

    Parameters
    ----------
    callback : CallbackQuery
        The callback initiated by the user when pressing the registration button.
    state : FSMContext
        The current state of the FSM used to update the list of players.
    """
    players = await get_players_set_from_state(state)

    user = callback.from_user

    if user not in players:
        players.add(user)
        await state.update_data(players=players)

        await callback.answer("Вы присоединились к игре! Для отмены нажмите кнопку 'Присоединиться' еще раз")
        await update_reg_msg(reg_msg=callback.message, players=players)

    else:
        players.remove(user)
        await state.update_data(players=players)

        await callback.answer("Вы покинули игру!")
        await update_reg_msg(reg_msg=callback.message, players=players)


async def update_reg_msg(reg_msg: Message, players: set[User]) -> None:
    """Updates the registration message to reflect the current list of players.

    This function modifies the text of the given message
    to include the updated list of players who have joined the game.
    If there are players in the game, their usernames will be listed in the message. If there are no players,
    only the initial registration message will be shown.

    Parameters
    ----------
    reg_msg : Message
        The message object that will be updated with the new text and inline keyboard.
        This is the message where the registration information is displayed.

    players : set[User]
        A set of `User` objects representing the players who have joined the game.
        Each `User` object must have a `username` attribute to be displayed in the message.
    """
    if len(players) >= 1:
        players_str = ""
        for player in players:
            player_str = get_player_username_or_firstname(player)
            players_str += f"{player_str}, "
        await reg_msg.edit_text(
            text=f"{settings.start_registration_msg}\n\nУже присоединилось {len(players)} человек:\n{players_str}",
            reply_markup=reg,
        )
    else:
        await reg_msg.edit_text(text=settings.start_registration_msg, reply_markup=reg)
