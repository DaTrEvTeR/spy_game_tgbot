from aiogram.types import CallbackQuery, Message, User

from core.config import bot
from routers.game_states import GameData
from routers.helpers import get_user_mention


async def register_vote(callback: CallbackQuery, game_data: GameData) -> None:
    """Registers a vote from a user in the game data.

    Parameters
    ----------
    callback : CallbackQuery
        The callback query containing the user information and vote data.
    game_data : GameData
        The game data object to update with the vote.
    """
    game_data.voted_players.add(callback.from_user)

    if callback.data in game_data.votes:
        game_data.votes[callback.data] += 1
    else:
        game_data.votes[callback.data] = 1
    await game_data.save()


async def send_confirmation_notification(callback: CallbackQuery) -> None:
    """Sends a confirmation notification to the user who cast the vote.

    Parameters
    ----------
    callback : CallbackQuery
        The callback query containing the information about the vote.
    """
    voted_for_name = await get_user_by_id(chat_id=callback.message.chat.id, user_id=int(callback.data))
    await callback.answer(f"Ваш голос за игрока {voted_for_name.first_name} учтен.")


async def get_user_by_id(chat_id: int | str, user_id: int) -> User:
    """Retrieves a user from a chat by their user ID.

    Parameters
    ----------
    chat_id : int | str
        The chat ID where the user is located.
    user_id : int
        The user ID of the user to retrieve.

    Returns:
    -------
    User
        The User object representing the user with the given ID.
    """
    voted_for = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
    return voted_for.user


async def show_results(vote_msg: Message, game_data: GameData) -> None:
    """Shows the results of the voting process.

    Parameters
    ----------
    vote_msg : Message
        The message where the voting results will be sent.
    game_data : GameData
        The game data object containing the voting results.
    """
    vote_results: str = ""
    for player_id, count in game_data.votes.items():
        voted_for = await get_user_by_id(chat_id=vote_msg.chat.id, user_id=int(player_id))
        vote_results += f"\n{get_user_mention(voted_for)}: {count}"
    await vote_msg.answer(f"Результаты голосования:\n{vote_results}")


def get_key(votes: dict, count: int) -> str:
    """Finds the player ID with the specified vote count.

    Parameters
    ----------
    votes : dict
        A dictionary of player IDs and their respective vote counts.
    count : int
        The vote count to match.

    Returns:
    -------
    str
        The player ID associated with the specified vote count.
    """
    for player_id, votes_count in votes.items():
        if votes_count == count:
            return player_id
    return ""
