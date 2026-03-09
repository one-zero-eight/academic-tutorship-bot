from aiogram_dialog import DialogManager

from src.bot.dialog_extension import extend_dialog
from src.bot.utils import *
from src.db.repositories import meeting_repo, tutor_repo
from src.domain.models import MeetingStatus


async def meetings_type_getter(dialog_manager: DialogManager, **kwargs):
    return {}


async def meetings_list_getter(dialog_manager: DialogManager, **kwargs):
    meetings = await meeting_repo.list_((MeetingStatus.ANNOUNCED, MeetingStatus.FINISHED))
    return {
        "meetings": meetings,
    }


async def meeting_info_getter(dialog_manager: DialogManager, **kwargs):
    manager = extend_dialog(dialog_manager)
    meeting = await manager.state.get_meeting()
    attendance = None
    if await meeting_repo.has_attendance(meeting.id):
        attendance = await meeting_repo.get_attendance(meeting.id)
    tutor = None
    if meeting.tutor_id:
        tutor = await tutor_repo.get(id=meeting.tutor_id)
    data = await user_status_getter(manager, **kwargs)
    data.update(
        {
            "title": meeting.title,
            "description": meeting.description,
            "status": meeting.status,
            "date": meeting.datetime_,
            "duration": meeting.duration_human,
            "room": meeting.room,
            "attendance": attendance.emails if attendance else None,
            "tutor": tutor,
        }  # type: ignore
    )
    return data
