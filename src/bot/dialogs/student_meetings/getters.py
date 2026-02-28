from aiogram_dialog import DialogManager

from src.bot.dialog_extension import extend_dialog
from src.bot.dto import *
from src.bot.filters import *
from src.bot.utils import *
from src.db.repositories import meetings_repo


async def meetings_type_getter(dialog_manager: DialogManager, **kwargs):
    return {}


async def meetings_list_getter(dialog_manager: DialogManager, **kwargs):
    manager = extend_dialog(dialog_manager)

    # NOTE: the meetings list is dependent on user status
    #       as the meetings are used by admins and tutors
    #       tutors can only see and work on meetings that
    #       are assigned to them
    user_status: UserStatus | None = await manager.state.get_value("status")
    if not user_status:
        raise ValueError("No status")

    meeting_statuses = {MeetingStatus.ANNOUNCED, MeetingStatus.CONDUCTING, MeetingStatus.FINISHED}

    meetings = []
    for status in meeting_statuses:
        meetings.extend(await meetings_repo.list(status=status))

    return {
        "meetings": meetings,
    }


async def meeting_info_getter(dialog_manager: DialogManager, **kwargs):
    manager = extend_dialog(dialog_manager)
    meeting = await manager.state.get_meeting()

    data = await user_status_getter(manager, **kwargs)
    data.update(
        {
            "title": meeting.title,
            "description": meeting.description,
            "status": meeting.status,
            "date": meeting.date_human,
            "duration": meeting.duration_human,
            "room": meeting.room if meeting.room else "---",
            "attendance_count": len(meeting.attendance) if meeting.attendance else None,
            "tutor_username": meeting.tutor.username if meeting.tutor else None,
        }  # type: ignore
    )
    return data
