from typing import Any

from aiogram.filters import Filter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, TelegramObject, User
from email_validator import validate_email
from email_validator.exceptions import EmailNotValidError

from src.db.repositories import student_repo, tutor_repo
from src.domain.models import UserStatus


async def get_user_roles(telegram_id: int) -> set[UserStatus]:
    roles: set[UserStatus] = set()

    roles.add(UserStatus.student)  # Any user is student

    if await tutor_repo.exists(telegram_id=telegram_id):
        roles.add(UserStatus.tutor)
    if await student_repo.is_admin(telegram_id=telegram_id):
        roles.add(UserStatus.admin)

    return roles


async def get_user_status(telegram_id: int) -> UserStatus:
    return _effective_status(await get_user_roles(telegram_id))


def _effective_status(roles: set[UserStatus]) -> UserStatus:
    if UserStatus.admin in roles:
        return UserStatus.admin
    if UserStatus.tutor in roles:
        return UserStatus.tutor
    return UserStatus.student


class UserAuthenticatedFilter(Filter):
    async def __call__(self, event: TelegramObject, event_from_user: User, state: FSMContext) -> bool | dict[str, Any]:
        return await state.get_value("authenticated", False)


class StatusFilter(Filter):
    def __init__(self, *statuses: UserStatus):
        self._statuses = frozenset(statuses)

    async def __call__(
        self, event: TelegramObject | None = None, event_from_user: User | None = None
    ) -> bool | dict[str, Any]:
        user = event_from_user or getattr(event, "from_user", None)
        if user is None:
            return False

        roles = await get_user_roles(user.id)

        if not self._statuses:
            return {"status": _effective_status(roles)}

        return bool(roles & self._statuses)


class EmailEnteredFilter(Filter):
    async def __call__(self, event: TelegramObject, event_from_user, state) -> bool | dict[str, Any]:
        try:
            if isinstance(event, Message) and event.text:
                validate_email(event.text)
                return True
        except EmailNotValidError:
            pass
        return False


USER_AUTHENTICATED_FILTER = UserAuthenticatedFilter()
EMAIL_ENTERED_FILTER = EmailEnteredFilter()
