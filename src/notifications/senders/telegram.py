from .base import NotificationSender


class TelegramSender(NotificationSender):
    async def send(self, user_id: int, text: str):
        raise NotImplementedError

    async def send_batch(self, user_ids: list[int], text: str):
        raise NotImplementedError
