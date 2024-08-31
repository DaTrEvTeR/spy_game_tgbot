import asyncio
import logging
from asyncio import CancelledError

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from core.settings import settings
from routers.start_game.helpers import get_players_set_from_state, is_players_enough
from routers.start_game.keyboards import reg
from routers.start_game.states import GameStates


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


async def start_registration(message: Message, state: FSMContext) -> None:
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

    reg_message = await message.answer(
        text="Началась регистрация на игру",
        reply_markup=reg,
    )

    await manage_registration_timer(reg_message=reg_message, state=state)


async def manage_registration_timer(reg_message: Message, state: FSMContext) -> None:
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
        if await is_players_enough(state=state):
            await start_game(reg_message=reg_message, state=state)
        else:
            await game_cancel(reg_message=reg_message, state=state)
    except CancelledError:
        await start_game(reg_message=reg_message, state=state)


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
    await reg_message.answer("*Игровой процесс*")


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

    user_id = callback.from_user.id

    if user_id not in players:
        players.add(user_id)
        await state.update_data(players=players)

        await callback.answer("Вы присоединились к игре! Для отмены нажмите кнопку 'Присоединиться' еще раз")

        logging.info(
            f"User {callback.from_user.username} - {callback.from_user.full_name} "
            f"- {callback.from_user.id} joined the game"
        )

    else:
        players.remove(user_id)
        await state.update_data(players=players)

        await callback.answer("Вы покинули игру!")

        logging.info(
            f"User {callback.from_user.username} - {callback.from_user.full_name} "
            f"- {callback.from_user.id} left the game"
        )
