from aiogram.types import CallbackQuery, Message, Update

from core.config import bot, dp


async def feed_callback(message: Message, data: str) -> None:
    """Simulate a callback query by creating and feeding a custom update to the dispatcher.

    This function manually constructs a `CallbackQuery` and wraps it inside an `Update`
    object, which is then processed by the dispatcher. It allows to simulate a
    callback query.

    Parameters
    ----------
    message : Message
        The message object representing the current chat message. This is used to extract
        information such as the user who sent the message and the chat where the message
        was sent.
    data : str
        The callback data string that simulates the callback query data. This string is
        passed as the `data` field of the `CallbackQuery`.

    """
    callback_query = CallbackQuery(
        id="manual",
        from_user=message.from_user,
        chat_instance=str(message.chat.id),
        message=message,
        data=data,
    )

    update = Update(update_id=1, callback_query=callback_query)

    await dp.feed_update(bot=bot, update=update)
