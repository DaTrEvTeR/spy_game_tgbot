from aiogram.types import User

from .get_user_mention import get_user_mention


def get_str_players_list(players: dict[int, User]) -> str:
    """Function to get all usernames or first names with order nums from dict of Users objects.

    Parameters
    ----------
    players : dict[User]
        Set with users.

    Returns:
    -------
    str
        String with all usernames or first names of players from set.
    """
    players_str = ""
    for num, player in players.items():
        player_str = get_user_mention(player)
        players_str += f"{num}. {player_str}\n"
    return players_str
