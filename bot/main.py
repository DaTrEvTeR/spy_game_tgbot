import asyncio
import logging
import sys

import handlers  # noqa: F401
from config import bot, dp

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(dp.start_polling(bot))
