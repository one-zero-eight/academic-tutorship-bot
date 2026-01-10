from typing import Any

from aiogram.filters import Filter
from aiogram.fsm.context import FSMContext
from aiogram.types import TelegramObject, User

from src.config import settings
from src.domain.models import UserStatus


class UserAuthenticatedFilter(Filter):
    async def __call__(self, event: TelegramObject, event_from_user: User, state: FSMContext) -> bool | dict[str, Any]:
        return await state.get_value("authenticated", False)


class StatusFilter(Filter):
    _status: UserStatus | None

    def __init__(self, status: UserStatus | None = None):
        self._status = status

    async def __call__(self, event: TelegramObject, event_from_user: User) -> bool | dict[str, Any]:
        telegram_id = event_from_user.id

        if telegram_id in settings.admins:
            status = UserStatus.admin
        elif False:  # TODO: add tutors check
            status = UserStatus.tutor
        else:
            status = UserStatus.student

        if self._status is None:
            return {"status": status}

        if status == self._status:
            return True
        return False


USER_AUTHENTICATED_FILTER = UserAuthenticatedFilter()
