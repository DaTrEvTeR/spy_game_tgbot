from aiogram import html
from aiogram.filters import CommandStart
from aiogram.types import Message
from config import dp


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """This handler receives messages with `/start` command."""
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")
