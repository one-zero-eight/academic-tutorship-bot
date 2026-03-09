from abc import ABC, abstractmethod


class NotificationSender(ABC):
    @abstractmethod
    async def send(self, user_id: int, text: str): ...

    @abstractmethod
    async def send_batch(self, user_ids: list[int], text: str): ...
