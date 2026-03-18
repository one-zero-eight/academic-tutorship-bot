from aiogram_dialog import DialogManager

from src.bot.dialog_extension import extend_dialog
from src.bot.exceptions import AuthorityException
from src.bot.filters import *
from src.bot.utils import *
from src.db.repositories import meeting_repo, tutor_repo
from src.domain.models import MeetingStatus


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

    match meetings_type:
        case "created":
            status_range = MeetingStatus.CREATED
        case "announced":
            status_range = (MeetingStatus.ANNOUNCED, MeetingStatus.FINISHED)
        case "closed":
            status_range = MeetingStatus.CLOSED
        case _:
            raise ValueError("Unknown meeting type")

    match user_status:
        case UserStatus.admin:
            meetings = await meeting_repo.get_list(status_range)
        case UserStatus.tutor:
            tutor = await tutor_repo.get(telegram_id=manager.chat.id)
            meetings = await meeting_repo.get_list(status_range, tutor_id=tutor.id)
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
            "can_see_tutor_profile": bool(tutor) and not is_assigned_tutor,
            "can_see_tutor_profile_control": is_assigned_tutor,
        }  # type: ignore
    )
    return data


async def meeting_create_getter(dialog_manager: DialogManager, **kwargs):
    manager = extend_dialog(dialog_manager)
    discipline = await manager.state.get_value("discipline", None)
    title = await manager.state.get_value("title", None)
    can_be_created = bool(title and discipline)
    return {
        "title": title if title else "Untitled",
        "discipline_name": discipline["name"] if discipline else "Not set",
        "can_be_created": can_be_created,
    }
