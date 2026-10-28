from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from src.bot.filters import StatusFilter, get_user_roles, get_user_status
from src.domain.models import UserStatus

USER = SimpleNamespace(id=42)


def _mock_roles(monkeypatch: pytest.MonkeyPatch, *, tutor: bool = False, admin: bool = False) -> None:
    monkeypatch.setattr("src.bot.filters.tutor_repo.exists", AsyncMock(return_value=tutor))
    monkeypatch.setattr("src.bot.filters.student_repo.is_admin", AsyncMock(return_value=admin))


@pytest.mark.asyncio
async def test_roles_of_student(monkeypatch):
    _mock_roles(monkeypatch)

    roles = await get_user_roles(USER.id)

    assert UserStatus.student in roles
    assert UserStatus.tutor not in roles
    assert UserStatus.admin not in roles
    assert await get_user_status(USER.id) == UserStatus.student


@pytest.mark.asyncio
async def test_roles_of_tutor(monkeypatch):
    _mock_roles(monkeypatch, tutor=True)

    assert UserStatus.tutor in await get_user_roles(USER.id)
    assert await get_user_status(USER.id) == UserStatus.tutor


@pytest.mark.asyncio
async def test_roles_of_admin(monkeypatch):
    _mock_roles(monkeypatch, admin=True)

    assert UserStatus.admin in await get_user_roles(USER.id)
    assert await get_user_status(USER.id) == UserStatus.admin


@pytest.mark.asyncio
async def test_roles_of_admin_tutor(monkeypatch):
    _mock_roles(monkeypatch, tutor=True, admin=True)

    roles = await get_user_roles(USER.id)

    assert UserStatus.tutor in roles
    assert UserStatus.admin in roles
    assert await get_user_status(USER.id) == UserStatus.admin


@pytest.mark.asyncio
async def test_status_filter_admin(monkeypatch):
    _mock_roles(monkeypatch, admin=True)

    assert await StatusFilter(UserStatus.admin)(event=None, event_from_user=USER) is True  # type: ignore
    assert await StatusFilter(UserStatus.tutor)(event=None, event_from_user=USER) is False  # type: ignore


@pytest.mark.asyncio
async def test_status_filter_tutor(monkeypatch):
    _mock_roles(monkeypatch, tutor=True)

    assert await StatusFilter(UserStatus.tutor)(event=None, event_from_user=USER) is True  # type: ignore
    assert await StatusFilter(UserStatus.admin)(event=None, event_from_user=USER) is False  # type: ignore


@pytest.mark.asyncio
async def test_status_filter_multi_status_accepts_admin_tutor(monkeypatch):
    _mock_roles(monkeypatch, tutor=True, admin=True)

    assert await StatusFilter(UserStatus.tutor)(event=None, event_from_user=USER) is True  # type: ignore
    assert await StatusFilter(UserStatus.tutor, UserStatus.admin)(event=None, event_from_user=USER) is True  # type: ignore


@pytest.mark.asyncio
async def test_status_filter_returns_status_when_no_status_requested(monkeypatch):
    _mock_roles(monkeypatch, tutor=True)

    assert await StatusFilter()(event=None, event_from_user=USER) == {"status": UserStatus.tutor}  # type: ignore


@pytest.mark.asyncio
async def test_status_filter_rejects_event_without_user(monkeypatch):
    _mock_roles(monkeypatch, admin=True)

    assert await StatusFilter(UserStatus.admin)(event=SimpleNamespace(), event_from_user=None) is False  # type: ignore
