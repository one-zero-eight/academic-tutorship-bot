from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from src.bot.dialogs.change_meeting import handles, logic
from src.bot.user_errors import MeetingIsApproving
from src.domain.models import Discipline, Meeting, MeetingStatus


@pytest.fixture
def discipline() -> Discipline:
    return Discipline(id=1, name="Advanced Programming", year=2, language="en", semester=2)


def _meeting(discipline: Discipline, status: MeetingStatus = MeetingStatus.ANNOUNCED) -> Meeting:
    return Meeting.model_validate(
        {
            "id": 1,
            "title": "Async Python Workshop",
            "discipline": discipline,
            "creator_id": 1,
            "created_at": datetime.now(),
            "status": status,
            "duration": 3600,
            "description": "Learn async programming in Python",
            "room": "Room 101",
            "datetime": datetime.now() + timedelta(days=5),
            "tutor_id": 2,
        }
    )


@pytest.fixture
def meeting(discipline: Discipline) -> Meeting:
    return _meeting(discipline)


@pytest.fixture
def reschedule(monkeypatch) -> AsyncMock:
    mock = AsyncMock()
    monkeypatch.setattr(logic, "update_meeting_schedule", mock)
    return mock


@pytest.fixture
def repo_update(monkeypatch) -> AsyncMock:
    mock = AsyncMock()
    monkeypatch.setattr(logic.meeting_repo, "update", mock)
    return mock


@pytest.mark.asyncio
async def test_date_change_reschedules_announced_meeting(meeting, reschedule, repo_update):
    new_datetime = datetime.now() + timedelta(days=2)

    schedule_updated = await logic.update_meeting_date_room(meeting, {"datetime": new_datetime.isoformat()})

    assert schedule_updated is True
    assert meeting.datetime_ == new_datetime
    repo_update.assert_awaited_once_with(meeting, ["datetime", "room"])
    reschedule.assert_awaited_once_with(meeting)


@pytest.mark.asyncio
async def test_room_only_change_does_not_reschedule(meeting, reschedule, repo_update):
    schedule_updated = await logic.update_meeting_date_room(meeting, {"room": "Room 202"})

    assert schedule_updated is False
    assert meeting.room == "Room 202"
    repo_update.assert_awaited_once_with(meeting, ["datetime", "room"])
    reschedule.assert_not_awaited()


@pytest.mark.asyncio
async def test_date_change_before_announce_does_not_reschedule(discipline, reschedule, repo_update):
    meeting = _meeting(discipline, MeetingStatus.CREATED)
    new_datetime = datetime.now() + timedelta(days=2)

    schedule_updated = await logic.update_meeting_date_room(meeting, {"datetime": new_datetime.isoformat()})

    assert schedule_updated is False
    assert meeting.datetime_ == new_datetime
    reschedule.assert_not_awaited()


@pytest.mark.asyncio
async def test_date_change_during_approval_is_blocked(discipline, reschedule, repo_update):
    meeting = _meeting(discipline, MeetingStatus.APPROVING)

    with pytest.raises(MeetingIsApproving):
        await logic.update_meeting_date_room(meeting, {"room": "Room 202"})

    repo_update.assert_not_awaited()
    reschedule.assert_not_awaited()


class _FakeState:
    def __init__(self, meeting: Meeting, meeting_update: dict):
        self.meeting = meeting
        self.data: dict = {"meeting_update": meeting_update}

    @asynccontextmanager
    async def sync_meeting(self):
        yield self.meeting

    async def get_value(self, key, default=None):
        return self.data.get(key, default)

    async def update_data(self, data: dict):
        self.data.update(data)


@pytest.mark.asyncio
async def test_save_rightaway_reschedules_and_clears_state(monkeypatch, meeting):
    new_datetime = datetime.now() + timedelta(days=2)
    state = _FakeState(meeting, {"datetime": new_datetime.isoformat(), "room": "Room 202"})
    manager = SimpleNamespace(state=state)
    query = SimpleNamespace(from_user=SimpleNamespace(id=42))

    update_date_room = AsyncMock()
    send_rightaway = AsyncMock()
    monkeypatch.setattr(handles, "extend_dialog", lambda m: manager)
    monkeypatch.setattr(handles, "update_meeting_date_room", update_date_room)
    monkeypatch.setattr(handles.notification_manager, "send_meeting_update_rightaway", send_rightaway)

    await handles.on_date_room_save_rightaway(query, None, manager)

    update_date_room.assert_awaited_once_with(meeting, {"datetime": new_datetime.isoformat(), "room": "Room 202"})
    send_rightaway.assert_awaited_once()
    assert state.data["meeting_update"] is None
