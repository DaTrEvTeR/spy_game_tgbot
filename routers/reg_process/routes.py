from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from core.settings import settings
from routers.helpers import GameData
from routers.reg_process.services import (
    check_null_state,
    game_cancel,
    manage_registration_timer,
    reg_button_logic,
    start_game,
    start_game_now_logic,
    start_registration,
)

reg_process_router = Router(name="start_game")
reg_process_router.message.filter(
    F.chat.type.in_({"group", "supergroup"}),
)


@reg_process_router.message(Command(settings.start_game_command))
async def registration_for_the_game(message: Message, state: FSMContext) -> None:
    """Start registration for the game.
    Give `settings.registration_time` min for registration.
    If there are less players than `settings.minimal_player_count` cancel the game,
    otherwise start the game process.

    Parameters
    ----------
    message : Message
        Message with command /{settings.start_game_command}
    """
    game_data = await GameData.init(state=state)
    if await check_null_state(message=message, game_data=game_data):
        reg_message = await start_registration(message=message, game_data=game_data)
        is_start_game = await manage_registration_timer(game_data=game_data)
        if is_start_game:
            await start_game(reg_message=reg_message, game_data=game_data)
        else:
            await game_cancel(reg_message=reg_message, game_data=game_data)


@reg_process_router.callback_query(F.data == "reg")
async def register_user(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle callback data "reg".

    Parameters
    ----------
    callback : CallbackQuery
        Callback with data "reg"
    """
    game_data = await GameData.init(state=state)
    await reg_button_logic(callback=callback, game_data=game_data)


@reg_process_router.callback_query(F.data == "rules")
async def show_rules(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle callback data "rules".

    Parameters
    ----------
    callback : CallbackQuery
        Callback with data "rules"
    """
    data = await state.get_data()
    is_rules_in_chat = data.get("is_rules_in_chat")
    if is_rules_in_chat:
        await callback.answer("Правила уже в чате!")
    else:
        await state.update_data(is_rules_in_chat=True)
        await callback.answer()
        await callback.message.answer(
            text=settings.game_rules,
        )


@reg_process_router.callback_query(F.data == "start_now")
async def start_game_now(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle callback data "start_now" to immediately start the game.

    Parameters
    ----------
    callback : CallbackQuery
        Callback with data "start_now"
    state : FSMContext
        The current state of the FSM used to manage the game process.
    """
    game_data = await GameData.init(state=state)
    await start_game_now_logic(callback=callback, game_data=game_data)
