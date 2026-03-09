from src.domain.models import Meeting

from .senders import NotificationSender


class NotificationManager:
    def __init__(self, sender: NotificationSender):
        self.__sender = sender

    async def send_meeting_updated(self, meeting: Meeting):
        await self.__sender.send_batch()
