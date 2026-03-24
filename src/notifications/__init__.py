from src.notifications.bot import notification_bot, notification_dp
from src.notifications.notification_manager import NotificationManager

notification_manager = NotificationManager(notification_bot, notification_dp)


def init_handlers():
    from src.notifications import handles  # noqa: F401


__all__ = ["NotificationManager", "notification_manager", "init_handlers"]
