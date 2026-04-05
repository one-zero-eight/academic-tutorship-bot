from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from src.bot.middlewares import AutoAuthMiddleware
from src.domain.models import Tutor, UserStatus


class _DummyState:
    def __init__(self):
        self.data = {}

    async def update_data(self, payload: dict):
        self.data.update(payload)


@pytest.mark.asyncio
async def test_update_status_clears_self_tutor_when_user_is_not_tutor(monkeypatch):
    middleware = AutoAuthMiddleware()
    state = _DummyState()
    state.data["self_tutor"] = {"id": 1}

    monkeypatch.setattr("src.bot.middlewares.tutor_repo.exists", AsyncMock(return_value=False))
    monkeypatch.setattr("src.bot.middlewares.student_repo.is_admin", AsyncMock(return_value=False))

    status = await middleware._update_status(
        event=SimpleNamespace(),
        data={
            "state": state,
            "event_chat": SimpleNamespace(id=42),
        },
    )

    assert status == UserStatus.student
    assert state.data["status"] == UserStatus.student
    assert state.data["self_tutor"] is None


@pytest.mark.asyncio
async def test_update_status_sets_self_tutor_when_user_is_tutor(monkeypatch):
    middleware = AutoAuthMiddleware()
    state = _DummyState()
    tutor = Tutor(id=10, telegram_id=42, first_name="Name", last_name="Surname")

    monkeypatch.setattr("src.bot.middlewares.tutor_repo.exists", AsyncMock(return_value=True))
    monkeypatch.setattr("src.bot.middlewares.tutor_repo.get", AsyncMock(return_value=tutor))
    monkeypatch.setattr("src.bot.middlewares.student_repo.is_admin", AsyncMock(return_value=False))

    status = await middleware._update_status(
        event=SimpleNamespace(),
        data={
            "state": state,
            "event_chat": SimpleNamespace(id=42),
        },
    )

    assert status == UserStatus.tutor
    assert state.data["status"] == UserStatus.tutor
    assert state.data["self_tutor"] == tutor.model_dump()
