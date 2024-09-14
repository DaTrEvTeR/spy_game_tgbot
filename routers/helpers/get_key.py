from typing import Any, Dict


def get_key(dictionary: Dict, value: Any) -> Any:  #  noqa: ANN401
    """Finds the player key with the specified value."""
    for player_id, votes_count in dictionary.items():
        if votes_count == value:
            return player_id
    return None
