import asyncio
import logging
from asyncio import CancelledError

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from core.settings import settings
from routers.start_game.helpers import get_players_set_from_state
from routers.start_game.keyboards import reg
from routers.start_game.states import GameStates


async def check_null_state(message: Message, state: FSMContext) -> bool:
    cur_state = await state.get_state()

    if cur_state == GameStates.game.state:
        await message.answer("Игра уже идет!")
        return False

    if cur_state == GameStates.registration.state:
        await message.answer("Регистрация уже началась!")
        return False

    return True


async def start_registration(message: Message, state: FSMContext) -> None:
    await state.set_state(GameStates.registration)
    await state.update_data(players=set())

    reg_message = await message.answer(
        text="Началась регистрация на игру",
        reply_markup=reg,
    )

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


async def is_players_enough(state: FSMContext) -> bool:
    players = await get_players_set_from_state(state)
    return len(players) >= settings.minimal_player_count


async def start_game(reg_message: Message, state: FSMContext) -> None:
    await reg_message.edit_text(text="Набрано нужное количество игроков. Игра начинается.", reply_markup=None)
    await state.set_state(GameStates.game)
    await reg_message.answer("*Игровой процесс*")


async def game_cancel(reg_message: Message, state: FSMContext) -> None:
    await reg_message.edit_text(text="Недостаточно игроков. Регистрация отменена.", reply_markup=None)
    await state.clear()


async def start_game_now_logic(callback: CallbackQuery, state: FSMContext) -> None:
    if await is_players_enough(state):
        data = await state.get_data()
        registration_task = data.get("registration_task")
        registration_task.cancel()
    else:
        await callback.answer(
            f"Минимальное количество игроков для начала игры: {settings.minimal_player_count}", show_alert=True
        )


async def reg_button_logic(callback: CallbackQuery, state: FSMContext) -> None:
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
