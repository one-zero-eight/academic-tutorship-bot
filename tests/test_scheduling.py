from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

import pytest

from src.domain.models import Discipline, Meeting, MeetingStatus
from src.scheduling.scheduling import _job_meeting_reminder, update_meeting_schedule


@pytest.fixture
def test_discipline():
    return Discipline(
        id=1,
        name="Advanced Programming",
        year=2,
        language="en",
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
