from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aiogram import Dispatcher

import logging

from utils.get_routers import get_routers


def init_routes(dp: "Dispatcher") -> None:
    for router in get_routers():
        dp.include_router(router)
        logging.info(f"Router {router} added")
