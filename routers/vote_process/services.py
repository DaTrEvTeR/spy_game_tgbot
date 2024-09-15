import asyncio

from aiogram.types import CallbackQuery, Message

from core.settings import settings
from routers.helpers import GameData, process_remaining_players
from routers.vote_process.helpers import (
    process_votes,
    register_vote,
    send_confirmation_notification,
    show_results,
)
from routers.vote_process.keyboards import users


async def send_voting_message(callback: CallbackQuery, game_data: GameData) -> Message:
    """Sends a message with an inline keyboard for voting to the chat.

    Parameters
    ----------
    callback : CallbackQuery
        The callback query containing the information to send the message.
    game_data : GameData
        The game data object used to generate the voting keyboard.

    Returns:
    -------
    Message
        The message object sent to the chat with the voting options.
    """
    await callback.message.answer(text="Больше половины игроков готовы дать ответ. \nКто же является шпионом?")
    keyboard = users(game_data)
    return await callback.message.answer(text="Кого вы подозреваете в шпионаже?", reply_markup=keyboard)


async def run_wait_task(game_data: GameData) -> None:
    """Runs a task that waits for a specified time and cancels if the condition is met.

    Parameters
    ----------
    game_data : GameData
        The game data object that may be updated if the voting condition is met.
    """
    timer = asyncio.create_task(asyncio.sleep(settings.vote_time))
    game_data.vote_task = timer
    await game_data.save()

    try:
        await timer
        return  # noqa: TRY300
    except asyncio.CancelledError:
        return


async def process_vote(callback: CallbackQuery, game_data: GameData) -> None:
    """Processes a user's vote and updates the game data accordingly.

    Parameters
    ----------
    callback : CallbackQuery
        The callback query containing the user's vote information.
    game_data : GameData
        The game data object to update with the vote.
    """
    player = callback.from_user

    if player not in game_data.order_dict.values():
        await callback.answer("Вы не в игре.")
        return

    if player in game_data.voted_players:
        await callback.answer("Вы уже проголосовали.")
        return

    await register_vote(callback=callback, game_data=game_data)
    await send_confirmation_notification(callback=callback, game_data=game_data)

    if len(game_data.voted_players) == len(game_data.order_dict):
        game_data.vote_task.cancel()  # type: ignore


async def process_vote_results(vote_msg: Message, game_data: GameData) -> None:
    """Processes and displays the results of the vote.

    Parameters
    ----------
    vote_msg : Message
        The message where the voting results will be displayed.
    game_data : GameData
        The game data object containing the voting results and player information.
    """
    await vote_msg.edit_text(text="Голосование завершено")
    await show_results(vote_msg, game_data)
    await process_votes(vote_msg, game_data)
    game_data.ready_to_vote = set()
    game_data.voted_players = set()
    game_data.votes = {}
    await process_remaining_players(vote_msg, game_data)
