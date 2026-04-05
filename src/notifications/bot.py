from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.config import settings

notification_dp = Dispatcher()
notification_bot = Bot(
    token=settings.notification_bot_token.get_secret_value(), default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
