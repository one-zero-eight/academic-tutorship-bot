from src.db.repositories import meeting_repo, tutor_repo
from src.domain.models import Meeting, MeetingStatus
from src.notifications import notification_manager
from src.scheduling.scheduling import update_meeting_schedule, wipe_meeting_schedule


async def create_meeting(title: str, discipline_id: int, creator_telegram_id: int):
    meeting = await meeting_repo.create(
        title=title, discipline_id=discipline_id, creator_telegram_id=creator_telegram_id
    )
    return meeting


async def send_for_approval(meeting: Meeting):
    if not meeting.tutor_id:
        raise ValueError("No tutor")
    meeting.status = MeetingStatus.APPROVING
    await meeting_repo.update(meeting, ["status"])
    tutor = await tutor_repo.get(id=meeting.tutor_id)
    await notification_manager.send_meeting_approve_request(meeting, tutor)


async def announce_meeting(meeting: Meeting):
    if not meeting.tutor_id:
        raise ValueError("No tutor")
    meeting.announce()
    await update_meeting_schedule(meeting)
    await meeting_repo.update(meeting, ["status"])
    tutor = await tutor_repo.get(id=meeting.tutor_id)
    await notification_manager.send_meeting_announced(meeting, tutor)


async def cancel_meeting(meeting: Meeting):
    await notification_manager.send_meeting_cancelled(meeting)
    await meeting_repo.remove(meeting.id)
    await wipe_meeting_schedule(meeting)


async def finish_meeting(meeting: Meeting):
    meeting.finish()
    meeting.adjust_duration_to_now()
    await meeting_repo.update(meeting)
    await wipe_meeting_schedule(meeting)
    await notification_manager.send_meeting_finished(meeting)
