from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from settings import settings

dp: Dispatcher = Dispatcher()
bot = Bot(token=settings.bot_api_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
