from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.config import settings
from src.notifications.bot_commands import router as commands_router
from src.notifications.notification_manager import NotificationManager

_notification_dispatcher = Dispatcher()
_notification_dispatcher.include_router(commands_router)

_notification_bot = Bot(
    token=settings.notification_bot_token.get_secret_value(), default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
notification_manager = NotificationManager(_notification_bot, _notification_dispatcher)


__all__ = ["NotificationManager", "notification_manager"]
