from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from routers.game_states import GameData, GameStates
from routers.vote_process.services import process_vote, process_vote_results, run_wait_task, send_voting_message

router = Router(name="vote_process")

router.message.filter(F.chat.type.in_({"group", "supergroup"}), GameStates.vote)


@router.callback_query(F.data == "start_vote")
async def init_game(callback: CallbackQuery, state: FSMContext) -> None:
    """Initializes the voting process by setting the game state to voting,
    sending the voting message, and starting the wait task.

    Parameters
    ----------
    callback : CallbackQuery
        The callback query containing the information to start the voting process.
    state : FSMContext
        The state context used to manage the game state and data.
    """
    game_data = await GameData.init(state=state)

    await game_data.state.set_state(GameStates.vote)
    vote_msg = await send_voting_message(callback=callback, game_data=game_data)

    await run_wait_task(game_data=game_data)
    await process_vote_results(vote_msg=vote_msg, game_data=game_data)


@router.callback_query()
async def handle_vote(callback: CallbackQuery, state: FSMContext) -> None:
    """Handles a user's vote by processing the callback query and updating the game data.

    Parameters
    ----------
    callback : CallbackQuery
        The callback query containing the user's vote information.
    state : FSMContext
        The state context used to manage the game data and handle the vote.
    """
    game_data = await GameData.init(state=state)

    await process_vote(callback=callback, game_data=game_data)
