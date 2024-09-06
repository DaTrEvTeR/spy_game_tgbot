from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

my_role = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Моя роль", callback_data="my_role")],
    ]
)
complete_msg = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Закончил", callback_data="finished")],
    ]
)
