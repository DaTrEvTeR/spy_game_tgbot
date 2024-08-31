from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from core.settings import settings
from routers.start_game.services import check_null_state, reg_button_logic, start_game_now_logic, start_registration

router = Router(name="start_game")
router.message.filter(
    F.chat.type.in_({"group", "supergroup"}),
)


@router.message(Command(settings.start_game_command))
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
    if await check_null_state(message, state):
        await start_registration(message, state)


@router.callback_query(F.data == "reg")
async def register_user(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle callback data "reg".

    Parameters
    ----------
    callback : CallbackQuery
        Callback with data "reg"
    """
    await reg_button_logic(callback, state)


@router.callback_query(F.data == "rules")
async def show_rules(callback: CallbackQuery) -> None:
    """Handle callback data "rules".

    Parameters
    ----------
    callback : CallbackQuery
        Callback with data "rules"
    """
    await callback.answer()
    await callback.message.answer(
        text=settings.game_rules,
    )


@router.callback_query(F.data == "start_now")
async def start_game_now(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle callback data "start_now" to immediately start the game.

    Parameters
    ----------
    callback : CallbackQuery
        Callback with data "start_now"
    state : FSMContext
        The current state of the FSM used to manage the game process.
    """
    await start_game_now_logic(callback, state)
