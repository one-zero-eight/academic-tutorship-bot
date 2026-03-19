import html
from datetime import datetime, timedelta

from aiogram_dialog import DialogManager

from src.bot.dialog_extension import extend_dialog
from src.bot.utils import *
from src.db.repositories import meeting_repo, tutor_repo
from src.domain.models import MeetingStatus


async def meetings_list_getter(dialog_manager: DialogManager, **kwargs):
    meetings = await meeting_repo.get_list((MeetingStatus.ANNOUNCED, MeetingStatus.FINISHED))
    meetings = _filter_meetings_by_date(meetings)
    meetings.sort(key=lambda m: (m.datetime_ is None, m.datetime_), reverse=False)
    meeting_items = [
        {
            "id": meeting.id,
            "display": f"[{meeting.datetime_}] {html.escape(meeting.title)}",
        }
        for meeting in meetings
    ]
    return {
        "meetings": meeting_items,
    }


def _filter_meetings_by_date(meetings: list[Meeting]) -> list[Meeting]:
    """Filter meetings  which finish date is within last 12 hours or later in future"""
    now = datetime.now()
    filtered = []
    for m in meetings:
        if m.datetime_ and (m.datetime_ + timedelta(seconds=m.duration)) > now:
            filtered.append(m)
    return filtered


async def meeting_info_getter(dialog_manager: DialogManager, **kwargs):
    manager = extend_dialog(dialog_manager)
    meeting = await manager.state.get_meeting()

    data = await user_status_getter(manager, **kwargs)
    is_admin: bool = data["is_admin"]
    tutor = await tutor_repo.get(id=meeting.tutor_id) if meeting.tutor_id else None
    is_assigned_tutor = bool(data["is_tutor"] and tutor and tutor.telegram_id == manager.chat.id)
    is_authorized = is_admin or is_assigned_tutor
    emails = None
    if await meeting_repo.has_attendance(meeting.id):
        emails = await meeting_repo.get_attendance(meeting.id)
    data.update(
        {
            "title": html.escape(meeting.title),
            "description": html.escape(meeting.description) if meeting.description else None,
            "discipline": meeting.discipline,
            "status": meeting.status,
            "date": meeting.datetime_,
            "duration": meeting.duration_human,
            "room": html.escape(meeting.room) if meeting.room else "---",
            "attendance_count": len(emails) if emails else None,
            "tutor_username": html.escape(tutor.username) if tutor and tutor.username else None,
            "can_be_changed": is_authorized and meeting.status < MeetingStatus.CLOSED,
            "can_be_announced": is_authorized and meeting.status == MeetingStatus.CREATED,
            "can_be_finished": is_authorized and meeting.status == MeetingStatus.CONDUCTING,
            "can_be_closed": is_authorized and meeting.status == MeetingStatus.FINISHED,
            "can_be_deleted": is_authorized,
            "can_see_attendance": is_authorized and meeting.status >= MeetingStatus.CLOSED,
            "can_see_tutor_profile": bool(tutor) and not is_assigned_tutor,
            "can_see_tutor_profile_control": bool(tutor) and is_assigned_tutor,
        }  # type: ignore
    )
    return data
