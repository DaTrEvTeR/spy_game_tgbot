from typing import TYPE_CHECKING, Set

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext


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
