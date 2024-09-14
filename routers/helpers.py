from typing import Any, Dict

from aiogram.types import User


def get_user_mention(player: User) -> str:
    """Generates a clickable mention of a Telegram user, which links to their profile.

    Parameters
    ----------
    player : User
        An instance of the `User` class representing a Telegram user.

    Returns:
    -------
    str
        An HTML string that formats the user's first name as a clickable hyperlink.
    """
    user_id = player.id
    first_name = player.first_name

    return f'<a href="tg://user?id={user_id}">{first_name}</a>'


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
        player_str = get_user_mention(player)
        players_str += f"{player_str}\n"
    return players_str


def get_key(dictionary: Dict, value: Any) -> Any:  #  noqa: ANN401
    """Finds the player key with the specified value."""
    for player_id, votes_count in dictionary.items():
        if votes_count == value:
            return player_id
    return None
