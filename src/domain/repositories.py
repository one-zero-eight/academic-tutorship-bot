from abc import ABC, abstractmethod

from .models import Tutor


class TutorsRepository(ABC):
    @abstractmethod
    async def exists(
        self,
        *,
        id: int | None = None,
        tg_id: int | None = None,
        username: str | None = None,
        tutor: Tutor | None = None,
    ) -> bool: ...

    @abstractmethod
    async def get(self, *, id: int | None = None, tg_id: int | None = None, username: str | None = None) -> Tutor: ...

    @abstractmethod
    async def list(self, *, offset: int = 0, limit: int | None = None) -> list[Tutor]: ...

    @abstractmethod
    async def create(
        self,
        *,
        tg_id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> Tutor: ...

    @abstractmethod
    async def update(self, tutor: Tutor): ...

    @abstractmethod
    async def remove(
        self,
        *,
        id: int | None = None,
        tg_id: int | None = None,
        username: str | None = None,
        tutor: Tutor | None = None,
    ) -> Tutor: ...

    @abstractmethod
    async def dispose(self): ...
