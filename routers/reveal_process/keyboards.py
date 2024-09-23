from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def locations(locs_nums: list) -> InlineKeyboardMarkup:
    """Creates an inline keyboard with buttons for each location in the game.

    Parameters
    ----------


    Returns:
    -------
    InlineKeyboardMarkup
        The inline keyboard markup with buttons for each location.
    """
    keyboard_builder = InlineKeyboardBuilder()

    for i in locs_nums:
        keyboard_builder.add(InlineKeyboardButton(text=str(i), callback_data=str(i)))

    return keyboard_builder.adjust(2).as_markup()
