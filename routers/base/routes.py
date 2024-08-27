from aiogram import Router, html
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router(name="start")


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """This handler receives messages with `/start` command."""
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")
