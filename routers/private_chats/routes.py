from aiogram import F, Router, html
from aiogram.filters import CommandStart
from aiogram.types import Message

from core.settings import settings
from routers.private_chats.keyboards import replykeyboard

private_chats_router = Router(name="private_chat_router")
private_chats_router.message.filter(
    F.chat.type == "private",
)


@private_chats_router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """This handler receives messages with the `/start` command and
    sends a personalized greeting to the user.

    Parameters
    ----------
    message : Message
        The message object that contains the user's message data. This includes
        details such as the command issued, user information, and chat data.
    """
    await message.answer(
        text=f"Hello, {html.bold(message.from_user.full_name)}!",
        reply_markup=replykeyboard,
    )


@private_chats_router.message(F.text == "Правила")
async def handle_rules(message: Message) -> None:
    """Handles the 'Правила' button press and sends the game rules.

    Parameters
    ----------
    message : Message
        Message object with "Правила" text
    """
    await message.answer(text=settings.game_rules)


@private_chats_router.message(F.text == "Список команд")
async def show_commands_list(message: Message) -> None:
    """Handles the 'Список команд' button press and sends the bot`s commands.

    Parameters
    ----------
    message : Message
        Message object with "Список команд" text
    """
    await message.answer(text=settings.commands)


@private_chats_router.message(F.text == "Как пользоваться ботом")
async def handle_how_to_use(message: Message) -> None:
    """Handles the 'Как пользоваться ботом' button press and sends instructions.

    Parameters
    ----------
    message : Message
    Message object with "Как пользоваться ботом" text
    """
    await message.answer(text=settings.how_use_bot)
