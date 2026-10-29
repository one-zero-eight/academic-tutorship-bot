from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.memory import MemoryStorage

from src.bot.constants import I18N_FORMAT_KEY
from src.bot.dialogs.change_meeting import handles as change_handles
from src.bot.dialogs.meetings import handles
from src.bot.dialogs.meetings.states import MeetingStates
from src.domain.models import Discipline, Meeting

USER = SimpleNamespace(id=42)


class FakeManager(SimpleNamespace):
    pass


def _manager(state: FSMContext) -> FakeManager:
    return FakeManager(
        middleware_data={
            "state": state,
            "event_chat": SimpleNamespace(id=1),
            I18N_FORMAT_KEY: lambda text, data: text,
        },
        switch_to=AsyncMock(),
    )


def _query() -> SimpleNamespace:
    return SimpleNamespace(answer=AsyncMock(), from_user=USER)


@pytest.fixture
def state() -> FSMContext:
    return FSMContext(storage=MemoryStorage(), key=StorageKey(bot_id=1, chat_id=1, user_id=1))


@pytest.fixture
def discipline() -> dict:
    return Discipline(id=5, name="Math", year=1, semester=1, language="EN").model_dump()


@pytest.mark.asyncio
async def test_create_submit_rejects_deleted_discipline(monkeypatch, state: FSMContext, discipline: dict):
    await state.update_data({"discipline": discipline, "title": "Stale"})
    monkeypatch.setattr(handles.discipline_repo, "exists", AsyncMock(return_value=False))
    create_meeting = AsyncMock()
    monkeypatch.setattr(handles, "create_meeting", create_meeting)
    query = _query()

    await handles.on_create_submit(query, None, _manager(state))

    create_meeting.assert_not_awaited()
    query.answer.assert_awaited_once_with("Q_MEETING_DISCIPLINE_NOT_FOUND", show_alert=True)
    assert await state.get_value("discipline") is None
    assert await state.get_value("title") == "Stale"


@pytest.mark.asyncio
async def test_create_submit_creates_meeting_for_live_discipline(monkeypatch, state: FSMContext, discipline: dict):
    await state.update_data({"discipline": discipline, "title": "Fresh"})
    monkeypatch.setattr(handles.discipline_repo, "exists", AsyncMock(return_value=True))
    meeting = Meeting(
        id=11,
        title="Fresh",
        discipline=Discipline(**discipline),
        creator_id=None,
        tutor_id=None,
    )
    create_meeting = AsyncMock(return_value=meeting)
    monkeypatch.setattr(handles, "create_meeting", create_meeting)
    manager = _manager(state)
    query = _query()

    await handles.on_create_submit(query, None, manager)

    create_meeting.assert_awaited_once_with("Fresh", discipline["id"], 1)
    manager.switch_to.assert_awaited_once_with(MeetingStates.info, None)
    assert await state.get_value("discipline") is None


@pytest.mark.asyncio
async def test_create_submit_without_input_does_not_crash(monkeypatch, state: FSMContext):
    monkeypatch.setattr(handles.discipline_repo, "exists", AsyncMock(return_value=True))
    create_meeting = AsyncMock()
    monkeypatch.setattr(handles, "create_meeting", create_meeting)
    query = _query()

    await handles.on_create_submit(query, None, _manager(state))

    create_meeting.assert_not_awaited()
    query.answer.assert_awaited_once()
    assert query.answer.await_args.kwargs["show_alert"] is True


@pytest.mark.asyncio
async def test_change_meeting_rejects_deleted_discipline(monkeypatch, state: FSMContext, discipline: dict):
    await state.update_data({"discipline": discipline})
    monkeypatch.setattr(change_handles.discipline_repo, "exists", AsyncMock(return_value=False))
    set_discipline = AsyncMock()
    monkeypatch.setattr(change_handles.meeting_repo, "set_discipline", set_discipline)
    query = _query()

    await change_handles.on_back_from_title_discipline_btn(query, None, _manager(state))

    set_discipline.assert_not_awaited()
    query.answer.assert_awaited_once_with("Q_MEETING_DISCIPLINE_NOT_FOUND", show_alert=True)
    assert await state.get_value("discipline") is None
