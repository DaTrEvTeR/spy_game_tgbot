from aiogram.types import User


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
    return f"@{player.username}" if player.username else player.first_name


def get_str_players_list(players: set[User]) -> str:
    players_str = ""
    for player in players:
        player_str = get_player_username_or_firstname(player)
        players_str += f"{player_str}, "
    return players_str
