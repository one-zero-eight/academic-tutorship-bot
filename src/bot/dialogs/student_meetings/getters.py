from aiogram_dialog import DialogManager

from src.bot.dialog_extension import extend_dialog
from src.bot.utils import *
from src.db.repositories import meeting_repo, tutor_repo
from src.domain.models import MeetingStatus


async def meetings_type_getter(dialog_manager: DialogManager, **kwargs):
    return {}


async def meetings_list_getter(dialog_manager: DialogManager, **kwargs):
    meetings = await meeting_repo.get_list((MeetingStatus.ANNOUNCED, MeetingStatus.FINISHED))
    return {
        "meetings": meetings,
    }


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
            "title": meeting.title,
            "description": meeting.description,
            "discipline": meeting.discipline,
            "status": meeting.status,
            "date": meeting.datetime_,
            "duration": meeting.duration_human,
            "room": meeting.room if meeting.room else "---",
            "attendance_count": len(emails) if emails else None,
            "tutor_username": tutor.username if tutor else None,
            "can_be_changed": is_authorized and meeting.status < MeetingStatus.CLOSED,
            "can_be_announced": is_authorized and meeting.status == MeetingStatus.CREATED,
            "can_be_finished": is_authorized and meeting.status == MeetingStatus.CONDUCTING,
            "can_be_closed": is_authorized and meeting.status == MeetingStatus.FINISHED,
            "can_be_deleted": is_authorized,
            "can_see_attendance": is_authorized and meeting.status >= MeetingStatus.CLOSED,
        }  # type: ignore
    )
    return data
