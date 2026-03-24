from datetime import datetime

from src.bot.logging_ import log_error, log_info
from src.db.repositories import meeting_repo, tutor_repo
from src.domain.models import Meeting, MeetingStatus
from src.notifications import notification_manager
from src.scheduling.scheduling import update_meeting_schedule, wipe_meeting_schedule


async def create_meeting(title: str, discipline_id: int, creator_telegram_id: int):
    try:
        meeting = await meeting_repo.create(
            title=title, discipline_id=discipline_id, creator_telegram_id=creator_telegram_id
        )
    except Exception as e:
        log_error("meeting.logic.create.failed", creator_telegram_id=creator_telegram_id, reason=str(e))
        raise
    log_info("meeting.logic.create.persisted", meeting_id=meeting.id, creator_telegram_id=creator_telegram_id)
    return meeting


async def send_for_approval(meeting: Meeting):
    if not meeting.tutor_id:
        raise ValueError("No tutor")
    try:
        meeting.status = MeetingStatus.APPROVING
        await meeting_repo.update(meeting, ["status"])
        tutor = await tutor_repo.get(id=meeting.tutor_id)
        await notification_manager.send_meeting_approve_request(meeting, tutor)
    except Exception as e:
        log_error("meeting.logic.approval.failed", meeting_id=meeting.id, reason=str(e))
        raise
    log_info("meeting.logic.approval.persisted_and_notified", meeting_id=meeting.id, tutor_id=meeting.tutor_id)


async def announce_meeting(meeting: Meeting):
    if not meeting.tutor_id:
        raise ValueError("No tutor")
    try:
        meeting.announce()
        await update_meeting_schedule(meeting)
        await meeting_repo.update(meeting, ["status"])
        tutor = await tutor_repo.get(id=meeting.tutor_id)
        await notification_manager.send_meeting_announced(meeting, tutor)
    except Exception as e:
        log_error("meeting.logic.announce.failed", meeting_id=meeting.id, reason=str(e))
        raise
    log_info("meeting.logic.announce.persisted_scheduled_notified", meeting_id=meeting.id, tutor_id=meeting.tutor_id)


async def approve_meeting(meeting: Meeting):
    assert meeting.tutor_id
    assert meeting.datetime_
    assert meeting.status == MeetingStatus.APPROVING
    if meeting.datetime_ < datetime.now():
        raise TimeoutError("Meeting date is in the past")
    try:
        meeting.approve()
        await update_meeting_schedule(meeting)
        await meeting_repo.update(meeting, ["status"])
        tutor = await tutor_repo.get(id=meeting.tutor_id)
        await notification_manager.send_meeting_approved(meeting)
        await notification_manager.send_meeting_announced(meeting, tutor)
    except Exception as e:
        log_error("meeting.logic.approve.failed", meeting_id=meeting.id, reason=str(e))
        raise
    log_info("meeting.logic.approve.persisted_scheduled_notified", meeting_id=meeting.id, tutor_id=meeting.tutor_id)


async def cancel_meeting(meeting: Meeting):
    try:
        await notification_manager.send_meeting_cancelled(meeting)
        await meeting_repo.remove(meeting.id)
        await wipe_meeting_schedule(meeting)
    except Exception as e:
        log_error("meeting.logic.cancel.failed", meeting_id=meeting.id, reason=str(e))
        raise
    log_info("meeting.logic.cancel.notified_removed_unscheduled", meeting_id=meeting.id)


async def finish_meeting(meeting: Meeting):
    try:
        meeting.finish()
        meeting.adjust_duration_to_now()
        await meeting_repo.update(meeting)
        await wipe_meeting_schedule(meeting)
        await notification_manager.send_meeting_finished(meeting)
    except Exception as e:
        log_error("meeting.logic.finish.failed", meeting_id=meeting.id, reason=str(e))
        raise
    log_info("meeting.logic.finish.persisted_unscheduled_notified", meeting_id=meeting.id)
