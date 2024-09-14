from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from routers.game_states import GameStates

router = Router(name="reveal_process")

router.message.filter(F.chat.type.in_({"group", "supergroup"}), GameStates.reveal)


@router.callback_query(F.data == "reveal_role")
async def init_game(callback: CallbackQuery, state: FSMContext) -> None:
    """Initializes the revealing process by setting the game state to reveal,
    sending the reveal user message, and start wait task.

    Parameters
    ----------
    callback : CallbackQuery
        The callback query containing the information to start the reveal process.
    state : FSMContext
        The state context used to manage the game state and data.
    """
