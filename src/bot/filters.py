from typing import Any

from aiogram.filters import Filter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, TelegramObject, User
from email_validator import validate_email
from email_validator.exceptions import EmailNotValidError

from src.db.repositories import student_repo, tutor_repo
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

        if await student_repo.is_admin(telegram_id=telegram_id):
            status = UserStatus.admin
        elif await tutor_repo.exists(telegram_id=telegram_id):
            status = UserStatus.tutor
        else:
            status = UserStatus.student

        if self._status is None:
            return {"status": status}

        if status == self._status:
            return True
        return False


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
