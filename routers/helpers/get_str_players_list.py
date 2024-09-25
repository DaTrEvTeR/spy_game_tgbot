from aiogram.types import User


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
        player_str = player.mention_html()
        players_str += f"{num}. {player_str}\n"
    return players_str
