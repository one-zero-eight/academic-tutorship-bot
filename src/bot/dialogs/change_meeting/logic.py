from datetime import date, datetime, time

from src.bot.logging_ import log_error, log_info, log_warning
from src.bot.user_errors import *
from src.db.repositories import meeting_repo, tutor_repo
from src.domain.models import Meeting, MeetingStatus, Tutor
from src.notifications import notification_manager
from src.scheduling.scheduling import update_meeting_schedule

MAX_ROOM_LEN = 64


async def update_meeting_title(meeting: Meeting, title: str):
    if meeting.status == MeetingStatus.APPROVING:
        log_warning("meeting.change.logic.title.blocked", meeting_id=meeting.id, reason="approving")
        raise MeetingIsApproving("Cannot change meeting while in APPROVING status")
    try:
        meeting.title = title
        await meeting_repo.update(meeting, ["title"])
    except Exception as e:
        log_error("meeting.change.logic.title.failed", meeting_id=meeting.id, reason=str(e))
        raise
    log_info("meeting.change.logic.title.persisted", meeting_id=meeting.id)
    # NOTE: do not notify on changed title (that's irrelevant)


async def update_meeting_date(meeting: Meeting, meeting_date: datetime):
    if meeting.status == MeetingStatus.APPROVING:
        log_warning("meeting.change.logic.date.blocked", meeting_id=meeting.id, reason="approving")
        raise MeetingIsApproving("Cannot change meeting while in APPROVING status")
    try:
        meeting.datetime_ = meeting_date
        await update_meeting_schedule(meeting)
        await meeting_repo.update(meeting, ["datetime"])
        await notification_manager.send_meeting_updated(meeting, "datetime")
    except Exception as e:
        log_error("meeting.change.logic.date.failed", meeting_id=meeting.id, reason=str(e))
        raise
    log_info("meeting.change.logic.date.persisted_scheduled_notified", meeting_id=meeting.id)


async def update_meeting_room(meeting: Meeting, room: str):
    if meeting.status == MeetingStatus.APPROVING:
        log_warning("meeting.change.logic.room.blocked", meeting_id=meeting.id, reason="approving")
        raise MeetingIsApproving("Cannot change meeting while in APPROVING status")
    try:
        meeting.room = room
        await meeting_repo.update(meeting, ["room"])
        await notification_manager.send_meeting_updated(meeting, "room")
    except Exception as e:
        log_error("meeting.change.logic.room.failed", meeting_id=meeting.id, reason=str(e))
        raise
    log_info("meeting.change.logic.room.persisted_notified", meeting_id=meeting.id)


async def update_meeting_duration(meeting: Meeting, selected_time: time):
    if meeting.status == MeetingStatus.APPROVING:
        log_warning("meeting.change.logic.duration.blocked", meeting_id=meeting.id, reason="approving")
        raise MeetingIsApproving("Cannot change meeting while in APPROVING status")
    try:
        meeting.duration = selected_time.hour * 3600 + selected_time.minute * 60
        await meeting_repo.update(meeting, ["duration"])
        schedule_updated = False
        if meeting.status > MeetingStatus.CREATED:
            await update_meeting_schedule(meeting)
            schedule_updated = True
    except Exception as e:
        log_error("meeting.change.logic.duration.failed", meeting_id=meeting.id, reason=str(e))
        raise
    log_info("meeting.change.logic.duration.persisted", meeting_id=meeting.id, schedule_updated=schedule_updated)
    # NOTE: do not notify on changed duration (that's irrelevant)


async def update_meeting_description(meeting: Meeting, description: str):
    if meeting.status == MeetingStatus.APPROVING:
        log_warning("meeting.change.logic.description.blocked", meeting_id=meeting.id, reason="approving")
        raise MeetingIsApproving("Cannot change meeting while in APPROVING status")
    try:
        meeting.description = description
        await meeting_repo.update(meeting, ["description"])
    except Exception as e:
        log_error("meeting.change.logic.description.failed", meeting_id=meeting.id, reason=str(e))
        raise
    log_info("meeting.change.logic.description.persisted", meeting_id=meeting.id)
    # NOTE: do not notify on changed description (that's irrelevant)


async def assign_tutor_to_meeting_by_telegram_id(meeting: Meeting, telegram_id: int) -> tuple[Tutor | None, Tutor]:
    if meeting.status == MeetingStatus.APPROVING:
        log_warning("meeting.change.logic.tutor_assign.blocked", meeting_id=meeting.id, reason="approving")
        raise MeetingIsApproving("Cannot change meeting while in APPROVING status")
    try:
        old_tutor = await tutor_repo.get(id=meeting.tutor_id) if meeting.tutor_id else None
        new_tutor = await tutor_repo.get(telegram_id=telegram_id)
        meeting.assign_tutor(new_tutor)
        await meeting_repo.update(meeting, ["tutor_id"])
        if old_tutor:
            await notification_manager.send_meeting_tutor_changed(meeting, old_tutor, new_tutor)
        else:
            await notification_manager.send_meeting_tutor_assigned(meeting, new_tutor)
    except Exception as e:
        log_error("meeting.change.logic.tutor_assign.failed", meeting_id=meeting.id, reason=str(e))
        raise
    log_info(
        "meeting.change.logic.tutor_assign.succeeded",
        meeting_id=meeting.id,
        old_tutor_id=old_tutor.id if old_tutor else None,
        new_tutor_id=new_tutor.id,
    )
    return old_tutor, new_tutor


async def assign_tutor_to_meeting_by_id(meeting: Meeting, tutor_id: int) -> tuple[Tutor | None, Tutor]:
    if meeting.status == MeetingStatus.APPROVING:
        log_warning("meeting.change.logic.tutor_assign.blocked", meeting_id=meeting.id, reason="approving")
        raise MeetingIsApproving("Cannot change meeting while in APPROVING status")
    try:
        old_tutor = await tutor_repo.get(id=meeting.tutor_id) if meeting.tutor_id else None
        new_tutor = await tutor_repo.get(id=tutor_id)
        meeting.assign_tutor(new_tutor)
        await meeting_repo.update(meeting, ["tutor_id"])
        if old_tutor:
            await notification_manager.send_meeting_tutor_changed(meeting, old_tutor, new_tutor)
        else:
            await notification_manager.send_meeting_tutor_assigned(meeting, new_tutor)
    except Exception as e:
        log_error("meeting.change.logic.tutor_assign.failed", meeting_id=meeting.id, reason=str(e))
        raise
    log_info(
        "meeting.change.logic.tutor_assign.succeeded",
        meeting_id=meeting.id,
        old_tutor_id=old_tutor.id if old_tutor else None,
        new_tutor_id=new_tutor.id,
    )
    return old_tutor, new_tutor


def combine_meeting_date_time(selected_date: date, selected_time: time):
    meeting_date = datetime.combine(selected_date, selected_time)
    if meeting_date < datetime.now():
        raise DateInPast()
    return meeting_date
