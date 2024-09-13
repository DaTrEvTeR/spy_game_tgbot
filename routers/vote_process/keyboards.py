from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from routers.game_states import GameData


def users(game_data: GameData) -> InlineKeyboardMarkup:
    """Creates an inline keyboard with buttons for each player in the game.

    Parameters
    ----------
    game_data : GameData
        The game data object containing the list of players.

    Returns:
    -------
    InlineKeyboardMarkup
        The inline keyboard markup with buttons for each player.
    """
    keyboard_builder = InlineKeyboardBuilder()

    for player in game_data.players:
        keyboard_builder.add(InlineKeyboardButton(text=player.first_name, callback_data=str(player.id)))

    return keyboard_builder.adjust(1).as_markup()
