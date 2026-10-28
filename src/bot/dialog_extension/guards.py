from collections.abc import Awaitable, Callable, Iterable
from functools import wraps
from typing import Any

from aiogram.filters import Filter
from aiogram.fsm.state import State
from aiogram.types import TelegramObject, User
from aiogram_dialog import Dialog, DialogManager
from aiogram_dialog.api.entities import Data
from aiogram_dialog.api.internal import WindowProtocol

from src.bot.exceptions import AuthorityException
from src.bot.filters import get_user_roles
from src.domain.models import UserStatus


class StatusGuard(Filter):
    """Status policy for a whole dialog branch."""

    def __init__(self, statuses: Iterable[UserStatus]):
        self._statuses = frozenset(statuses)

    async def is_allowed(self, telegram_id: int) -> bool:
        roles = await get_user_roles(telegram_id)
        return bool(roles & self._statuses)

    async def __call__(self, event: TelegramObject | None = None, event_from_user: User | None = None) -> bool:
        user = event_from_user or getattr(event, "from_user", None)
        if user is None:
            return False
        return await self.is_allowed(user.id)


class StatusGuardedDialog(Dialog):
    """Dialog that checks the user status on every event and when the dialog is started."""

    def __init__(self, *windows: WindowProtocol, guard: StatusGuard, **kwargs: Any):
        super().__init__(*windows, **kwargs)
        self._guard = guard
        for observer in self.observers.values():
            observer.filter(guard)

    async def process_start(self, manager: DialogManager, start_data: Data, state: State | None = None) -> None:
        event_from_user: User | None = manager.middleware_data.get("event_from_user")
        if event_from_user is not None and not await self._guard.is_allowed(event_from_user.id):
            raise AuthorityException(f"User {event_from_user.id} is not allowed to open {self.states_group_name()}")
        await super().process_start(manager, start_data, state)


def require_status(
    *statuses: UserStatus, forbidden: Iterable[UserStatus] = ()
) -> Callable[[Callable[..., Awaitable[Any]]], Callable[..., Awaitable[Any]]]:
    """Guard a widget handler (`on_click`, `MessageInput`, `Select`) with a status check."""

    allowed = frozenset(statuses)
    denied = frozenset(forbidden)

    def decorator(handler: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        @wraps(handler)
        async def wrapper(event: TelegramObject, *args: Any, **kwargs: Any) -> Any:
            user = getattr(event, "from_user", None)
            if user is None:
                raise AuthorityException(f"Cannot resolve the author of {handler.__name__}")

            roles = await get_user_roles(user.id)
            if not roles & allowed or roles & denied:
                raise AuthorityException(f"User {user.id} is not allowed to call {handler.__name__}")

            return await handler(event, *args, **kwargs)

        return wrapper

    return decorator
