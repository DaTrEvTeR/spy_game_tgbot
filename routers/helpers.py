from typing import Set

from aiogram.fsm.context import FSMContext
from aiogram.types import User

from core.settings import settings


async def get_players_set_from_state(state: "FSMContext") -> Set[int]:
    """The function is get set of users id from chat state, if there is no registered userd - set will be empty.

    Parameters
    ----------
    state : FSMContext
        Current state object of chat

    Returns:
    -------
    Set[int]
        Set with id of registered users or empty
    """
    data = await state.get_data()
    players: set = data.get("players", set())
    return players


async def is_players_enough(state: FSMContext) -> bool:
    """Check if the number of registered players is enough to start the game.

    This function retrieves the current set of players from the game state and checks
    whether their number meets or exceeds the minimum required to start the game.

    Parameters
    ----------
    state : FSMContext
        The current game state used to track ongoing processes and data.

    Returns:
    -------
    bool
        True if the number of players is equal to or greater than the required minimum, False otherwise.
    """
    players = await get_players_set_from_state(state)
    return len(players) >= settings.minimal_player_count


def get_player_username_or_firstname(player: User) -> str:
    """Function to get username or first name from User object.

    Parameters
    ----------
    player : User
        User object of player, which needed to get username|first_name

    Returns:
    -------
    str
        Returns a representation of the user as "@username" if the username is available, or "first_name" otherwise.
    """
    return f"@{player.username}" if player.username else str(player.first_name)
