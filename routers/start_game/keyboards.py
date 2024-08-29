from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

reg = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Присоединиться", callback_data="reg")],
        [InlineKeyboardButton(text="Правила", callback_data="rules")],
    ],
)
