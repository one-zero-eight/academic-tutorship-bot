from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

import pytest
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger

from src.domain.models import Discipline, Meeting, MeetingStatus
from src.scheduling.scheduling import (
    _job_meeting_reminder,
    meeting_job_ids,
    restore_meeting_schedules,
    update_meeting_schedule,
)


@pytest.fixture
def test_discipline():
    return Discipline(
        id=1,
        name="Advanced Programming",
        year=2,
        language="en",
        semester=2,
    )


@pytest.fixture
def test_meeting(test_discipline):
    return Meeting.model_validate(
        {
            "id": 1,
            "title": "Async Python Workshop",
            "discipline": test_discipline,
            "creator_id": 1,
            "created_at": datetime.now(),
            "status": MeetingStatus.ANNOUNCED,
            "duration": 3600,
            "description": "Learn async programming in Python",
            "room": "Room 101",
            "datetime": datetime.now() + timedelta(days=2),
            "tutor_id": 2,
        }
    )


@pytest.mark.asyncio
async def test_update_meeting_schedule_adds_reminder_jobs(test_meeting):
    with patch("src.scheduling.scheduling.scheduler") as mock_scheduler:
        await update_meeting_schedule(test_meeting)

    scheduled_job_ids = {call.kwargs["id"] for call in mock_scheduler.add_job.call_args_list}

    assert f"remind_24h_meeting_{test_meeting.id}" in scheduled_job_ids
    assert f"remind_1h_meeting_{test_meeting.id}" in scheduled_job_ids
    assert f"conduct_meeting_{test_meeting.id}" in scheduled_job_ids
    assert f"finish_meeting_{test_meeting.id}" in scheduled_job_ids


@pytest.mark.asyncio
async def test_update_meeting_schedule_skips_expired_24h_reminder(test_meeting):
    test_meeting.datetime_ = datetime.now() + timedelta(hours=2)

    with patch("src.scheduling.scheduling.scheduler") as mock_scheduler:
        await update_meeting_schedule(test_meeting)

    scheduled_job_ids = {call.kwargs["id"] for call in mock_scheduler.add_job.call_args_list}

    assert f"remind_24h_meeting_{test_meeting.id}" not in scheduled_job_ids
    assert f"remind_1h_meeting_{test_meeting.id}" in scheduled_job_ids


@pytest.mark.asyncio
async def test_job_meeting_reminder_sends_only_for_announced(test_meeting):
    with patch("src.scheduling.scheduling.meeting_repo") as mock_meeting_repo:
        mock_meeting_repo.get = AsyncMock(return_value=test_meeting)
        with patch("src.scheduling.scheduling.notification_manager") as mock_notification_manager:
            mock_notification_manager.send_meeting_reminder = AsyncMock()

            await _job_meeting_reminder(test_meeting.id, "1h")

            mock_notification_manager.send_meeting_reminder.assert_awaited_once_with(
                test_meeting,
                reminder_kind="1h",
            )


@pytest.mark.asyncio
async def test_job_meeting_reminder_skips_non_announced(test_meeting):
    test_meeting.status = MeetingStatus.CONDUCTING

    with patch("src.scheduling.scheduling.meeting_repo") as mock_meeting_repo:
        mock_meeting_repo.get = AsyncMock(return_value=test_meeting)
        with patch("src.scheduling.scheduling.notification_manager") as mock_notification_manager:
            mock_notification_manager.send_meeting_reminder = AsyncMock()

            await _job_meeting_reminder(test_meeting.id, "1h")

            mock_notification_manager.send_meeting_reminder.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_meeting_schedule_wipes_before_adding(test_meeting):
    with patch("src.scheduling.scheduling.scheduler") as mock_scheduler:
        await update_meeting_schedule(test_meeting)

    call_names = [name for name, _, _ in mock_scheduler.mock_calls]
    assert "remove_job" in call_names
    assert call_names.index("remove_job") < call_names.index("add_job")

    removed_job_ids = {call.args[0] for call in mock_scheduler.remove_job.call_args_list}
    assert removed_job_ids == set(meeting_job_ids(test_meeting.id))


@pytest.mark.asyncio
async def test_update_meeting_schedule_removes_stale_24h_reminder(test_meeting):
    test_meeting.datetime_ = datetime.now() + timedelta(hours=2)

    with patch("src.scheduling.scheduling.scheduler") as mock_scheduler:
        await update_meeting_schedule(test_meeting)

    removed_job_ids = {call.args[0] for call in mock_scheduler.remove_job.call_args_list}
    added_job_ids = {call.kwargs["id"] for call in mock_scheduler.add_job.call_args_list}

    stale_id = f"remind_24h_meeting_{test_meeting.id}"
    assert stale_id in removed_job_ids
    assert stale_id not in added_job_ids


@pytest.mark.asyncio
async def test_update_meeting_schedule_conducting_only_schedules_finish(test_meeting):
    test_meeting.status = MeetingStatus.CONDUCTING

    with patch("src.scheduling.scheduling.scheduler") as mock_scheduler:
        await update_meeting_schedule(test_meeting)

    removed_job_ids = {call.args[0] for call in mock_scheduler.remove_job.call_args_list}
    added_job_ids = {call.kwargs["id"] for call in mock_scheduler.add_job.call_args_list}

    assert f"conduct_meeting_{test_meeting.id}" in removed_job_ids
    assert added_job_ids == {f"finish_meeting_{test_meeting.id}"}


@pytest.mark.asyncio
async def test_update_meeting_schedule_below_announced_wipes_only(test_meeting):
    test_meeting.status = MeetingStatus.CREATED

    with patch("src.scheduling.scheduling.scheduler") as mock_scheduler:
        await update_meeting_schedule(test_meeting)

    removed_job_ids = {call.args[0] for call in mock_scheduler.remove_job.call_args_list}
    assert removed_job_ids == set(meeting_job_ids(test_meeting.id))
    mock_scheduler.add_job.assert_not_called()


@pytest.mark.asyncio
async def test_restore_meeting_schedules_reschedules_all(test_meeting):
    other_meeting = test_meeting.model_copy(update={"id": test_meeting.id + 1})

    with (
        patch("src.scheduling.scheduling.meeting_repo") as mock_meeting_repo,
        patch("src.scheduling.scheduling.update_meeting_schedule", new=AsyncMock()) as mock_update,
    ):
        mock_meeting_repo.get_list = AsyncMock(return_value=[test_meeting, other_meeting])

        await restore_meeting_schedules()

    mock_meeting_repo.get_list.assert_awaited_once_with((MeetingStatus.ANNOUNCED, MeetingStatus.FINISHED))
    assert [call.args[0] for call in mock_update.await_args_list] == [test_meeting, other_meeting]


@pytest.mark.asyncio
async def test_update_meeting_schedule_removes_stale_job_from_real_scheduler(test_meeting):
    real_scheduler = AsyncIOScheduler()
    stale_job_id = f"remind_24h_meeting_{test_meeting.id}"
    real_scheduler.add_job(
        func=_job_meeting_reminder,
        trigger=DateTrigger(datetime.now() + timedelta(days=1)),
        args=[test_meeting.id, "24h"],
        id=stale_job_id,
    )
    assert real_scheduler.get_job(stale_job_id) is not None

    test_meeting.datetime_ = datetime.now() + timedelta(hours=2)
    with patch("src.scheduling.scheduling.scheduler", real_scheduler):
        await update_meeting_schedule(test_meeting)

    assert real_scheduler.get_job(stale_job_id) is None
    assert real_scheduler.get_job(f"remind_1h_meeting_{test_meeting.id}") is not None
    assert real_scheduler.get_job(f"conduct_meeting_{test_meeting.id}") is not None
    assert real_scheduler.get_job(f"finish_meeting_{test_meeting.id}") is not None
