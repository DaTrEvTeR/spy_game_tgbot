from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from routers.helpers import GameData, GameStates
from routers.reveal_process.services import process_reveal_command, process_spy_answer

reveal_process_router = Router(name="reveal_process")

reveal_process_router.message.filter(F.chat.type.in_({"group", "supergroup"}), GameStates.reveal)


@reveal_process_router.callback_query(F.data == "reveal_role")
async def init_reveal(callback: CallbackQuery, state: FSMContext) -> None:
    """Initializes the revealing process by setting the game state to reveal,
    sending the reveal user message, and start wait task.

    Parameters
    ----------
    callback : CallbackQuery
        The callback query containing the information to start the reveal process.
    state : FSMContext
        The state context used to manage the game state and data.
    """
    game_data = await GameData.init(state=state)
    await process_reveal_command(callback, game_data)


@reveal_process_router.callback_query(GameStates.reveal)
async def spy_answer(callback: CallbackQuery, state: FSMContext) -> None:
    """Handles the spy's attempt to guess the game's location during the 'reveal' phase.

    This function is triggered when a spy attempts to guess the location. If it's the correct spy's turn, it either
    announces a win if the spy guesses correctly, or continues the game process if the guess is incorrect.

    Parameters
    ----------
    callback : CallbackQuery
        The callback query object from aiogram that contains information about the interaction.
    state : FSMContext
        The FSMContext object representing the current state of the game, holding game data.
    """
    if callback.data.isdigit():
        game_data = await GameData.init(state=state)

        if callback.from_user != game_data.reaveled_spy:
            await callback.answer("Сейчас не ваш ход!")
            return

        await process_spy_answer(callback, game_data)
    else:
        await callback.answer()
