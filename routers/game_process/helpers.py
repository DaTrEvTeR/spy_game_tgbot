from random import choice, shuffle

from aiogram.types import User

from core.settings import settings
from routers.game_states import GameData
from routers.helpers import get_user_mention


def get_asnwerer(game_data: GameData) -> str:
    """Retrieves the username or first name of the next player in the order list who will answer the question.

    If the current player is not the last one in the order list, the next player is selected.
    Otherwise, the first player in the list is chosen.

    Parameters
    ----------
    game_data : GameData
        The current game data containing the player order.

    Returns:
    -------
    str
        The username or first name of the player who will answer the question.
    """
    if game_data.cur_order_user_index != len(game_data.order_list) - 1:
        answerer = get_user_mention(game_data.order_list[game_data.cur_order_user_index + 1])
    else:
        answerer = get_user_mention(game_data.order_list[0])
    return answerer


def set_players_order(game_data: GameData) -> list[User]:
    """Shuffles and returns the list of players to define the turn order.

    Parameters
    ----------
    game_data : GameData
        The current game data containing the list of players.

    Returns:
    -------
    list[User]
        A shuffled list of players representing the order in which they will take turns.
    """
    order: list[User] = list(game_data.players)
    shuffle(order)
    return order


def set_spies(game_data: GameData) -> set[User]:
    """Randomly selects spies from the list of players.

    The number of spies is determined by dividing the total number of players by the
    minimal player count setting.

    Parameters
    ----------
    game_data : GameData
        The current game data containing the list of players.

    Returns:
    -------
    set[User]
        A set of users who have been selected as spies.
    """
    count_of_spies: int = len(game_data.players) // settings.minimal_player_count
    players_list = list(game_data.players.copy())
    spies = set()
    for _ in range(count_of_spies):
        spy = choice(players_list)
        spies.add(spy)
        players_list.remove(spy)
    return spies
