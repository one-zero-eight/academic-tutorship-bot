from datetime import datetime

from aiogram_dialog import DialogManager

from src.bot.dto import *
from src.bot.exceptions import AuthorityException
from src.bot.filters import *
from src.bot.utils import *
from src.db.repositories import meetings_repo, tutors_repo


async def meetings_list_getter(dialog_manager: DialogManager, **kwargs):
    state = get_state(dialog_manager)
    meetings_type: str = await state.get_value("meetings_type", "")

    # NOTE: the meetings list is dependent on user status
    #       as the meetings are used by admins and tutors
    #       tutors can only see and work on meetings that
    #       are assigned to them
    user_status: UserStatus | None = await state.get_value("status")
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
            chat: Chat = dialog_manager.middleware_data["event_chat"]
            tutor = await tutors_repo.get(tg_id=chat.id)
            for status in meeting_statuses:
                meetings.extend(await meetings_repo.list(status=status, tutor_id=tutor.id))

        case _:
            raise AuthorityException(f"Meetings list is inaccessible for {user_status}")

    return {
        "meetings_type": meetings_type.capitalize(),
        "meetings": meetings,
    }


async def meeting_info_getter(dialog_manager: DialogManager, **kwargs):
    state = get_state(dialog_manager)
    meeting = dto_to_meeting(await state.get_value("meeting"))

    if not meeting:
        raise ValueError("No Meeting in meeting_info_getter")

    date_to_str = lambda x: datetime.fromtimestamp(x).strftime("%d.%m.%Y %H:%M")  # noqa E731
    duration_to_str = lambda x: f"{x // 3600:02d}:{(x % 3600) // 60:02d}"  # noqa E731

    data = await user_status_getter(dialog_manager, **kwargs)
    is_admin: bool = data["is_admin"]
    data.update(
        {
            "title": meeting.title,
            "description": meeting.description,
            "status": meeting.status,
            "date": date_to_str(meeting.date) if meeting.date else "--.--.----",
            "duration": duration_to_str(meeting.duration) if meeting.duration else "--:--",
            "tutor_username": meeting.tutor.username if meeting.tutor else None,
            "can_be_announced": is_admin and meeting.status == MeetingStatus.CREATED,
            "can_be_deleted": is_admin,
        }  # type: ignore
    )
    return data
