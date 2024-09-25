from aiogram.types import User


def get_str_players_from_set(players: set[User]) -> str:
    """Function to get all usernames or first names from set of Users objects.

    Parameters
    ----------
    players : set[User]
        Set with users.

    Returns:
    -------
    str
        String with all usernames or first names of players from set.
    """
    players_str = ""
    for player in players:
        player_str = player.mention_html()
        players_str += f"{player_str}\n"
    return players_str
