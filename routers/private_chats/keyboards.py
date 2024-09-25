from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

replykeyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Правила")],
        [KeyboardButton(text="Как пользоваться ботом")],
        [KeyboardButton(text="Список команд")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Use menu",
)
