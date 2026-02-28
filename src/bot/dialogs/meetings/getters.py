from aiogram_dialog import DialogManager

from src.bot.dialog_extension import extend_dialog
from src.bot.dto import *
from src.bot.exceptions import AuthorityException
from src.bot.filters import *
from src.bot.utils import *
from src.db.repositories import meetings_repo, tutors_repo


async def meetings_type_getter(dialog_manager: DialogManager, **kwargs):
    data = await user_status_getter(dialog_manager, **kwargs)
    data.update(
        {
            "can_see_created": data["is_tutor"] or data["is_admin"],
            "can_see_closed": data["is_tutor"] or data["is_admin"],
            "can_see_announced": True,  # anybody can
        }
    )
    return data


async def meetings_list_getter(dialog_manager: DialogManager, **kwargs):
    manager = extend_dialog(dialog_manager)
    meetings_type: str = await manager.state.get_value("meetings_type", "")

    # NOTE: the meetings list is dependent on user status
    #       as the meetings are used by admins and tutors
    #       tutors can only see and work on meetings that
    #       are assigned to them
    user_status: UserStatus | None = await manager.state.get_value("status")
    if not user_status:
        raise ValueError("No status")

    if meetings_type == "created":
        meeting_statuses = {MeetingStatus.CREATED}
    elif meetings_type == "announced":
        meeting_statuses = {MeetingStatus.ANNOUNCED, MeetingStatus.CONDUCTING, MeetingStatus.FINISHED}
    elif meetings_type == "closed":
        meeting_statuses = {MeetingStatus.CLOSED}
    else:
        meeting_statuses = set()

    meetings = []
    match user_status:
        case UserStatus.admin:
            for status in meeting_statuses:
                meetings.extend(await meetings_repo.list(status=status))
        case UserStatus.tutor:
            tutor = await tutors_repo.get(tg_id=manager.chat.id)
            for status in meeting_statuses:
                meetings.extend(await meetings_repo.list(status=status, tutor_id=tutor.id))
        case _:
            raise AuthorityException(f"Meetings list is inaccessible for {user_status}")

    return {
        "meetings_type": meetings_type.capitalize(),
        "meetings": meetings,
    }


async def meeting_info_getter(dialog_manager: DialogManager, **kwargs):
    manager = extend_dialog(dialog_manager)
    meeting = await manager.state.get_meeting()

    data = await user_status_getter(manager, **kwargs)
    is_admin: bool = data["is_admin"]
    is_assigned_tutor = bool(data["is_tutor"] and meeting.tutor and manager.chat.id == meeting.tutor.tg_id)
    is_authorized = is_admin or is_assigned_tutor
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
            "can_be_changed": is_authorized and meeting.status < MeetingStatus.CLOSED,
            "can_be_announced": is_authorized and meeting.status == MeetingStatus.CREATED,
            "can_be_finished": is_authorized and meeting.status == MeetingStatus.CONDUCTING,
            "can_be_closed": is_authorized and meeting.status == MeetingStatus.FINISHED,
            "can_be_deleted": is_authorized,
            "can_see_attendance": is_authorized and meeting.status >= MeetingStatus.CLOSED,
        }  # type: ignore
    )
    return data
