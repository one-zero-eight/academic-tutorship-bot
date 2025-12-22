from abc import ABC, abstractmethod

from .models import Tutor


class TutorsRepository(ABC):
    @abstractmethod
    async def exists(
        self,
        *,
        id: int | None = None,
        telegram_id: int | None = None,
        tutor: Tutor | None = None,
    ) -> bool: ...

    @abstractmethod
    async def get(self, *, id: int | None = None, telegram_id: int | None = None) -> Tutor: ...

    @abstractmethod
    async def update(self, tutor: Tutor): ...
