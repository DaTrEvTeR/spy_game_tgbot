import asyncio
import logging
import sys

from core.config import bot, dp
from utils.init_routes import init_routes


def main() -> None:
    """Do all the steps to run the bot, such as setting up the logging config,
    register all routers from "routers" and run the bot.
    """
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    init_routes(dp=dp)
    asyncio.run(dp.start_polling(bot))
