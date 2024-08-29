from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.strategy import FSMStrategy

from core.settings import settings

dp: Dispatcher = Dispatcher(fsm_strategy=FSMStrategy.CHAT)
bot = Bot(token=settings.bot_api_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
