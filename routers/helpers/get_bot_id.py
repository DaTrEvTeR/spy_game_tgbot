from core.config import bot


async def get_bot_id() -> int:
    """Func to get bot`s id.

    Returns:
        Bot`s id
    """
    bot_id = await bot.get_me()
    return bot_id.id
