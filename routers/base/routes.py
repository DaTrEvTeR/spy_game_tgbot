from aiogram import Router, html
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router(name="start")


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """This handler receives messages with the `/start` command and
    sends a personalized greeting to the user.

    Parameters
    ----------
    message : Message
        The message object that contains the user's message data. This includes
        details such as the command issued, user information, and chat data.
    """
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")
