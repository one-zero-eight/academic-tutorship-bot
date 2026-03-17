from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.config import settings
from src.notifications.notification_manager import NotificationManager

notification_bot = Bot(
    token=settings.notification_bot_token.get_secret_value(), default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
notification_manager = NotificationManager(notification_bot)


__all__ = ["NotificationManager", "notification_manager"]
