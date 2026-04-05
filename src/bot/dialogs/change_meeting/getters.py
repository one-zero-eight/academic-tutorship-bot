import html
from datetime import datetime

from aiogram_dialog import DialogManager

from src.bot.dialog_extension import extend_dialog
from src.bot.filters import *
from src.bot.utils import *
from src.db.repositories import tutor_repo
from src.domain.models import Discipline, MeetingStatus


async def meeting_info_with_tutors_getter(dialog_manager: DialogManager, **kwargs):
    manager = extend_dialog(dialog_manager)
    meeting = await manager.state.get_meeting()
    tutors = await tutor_repo.get_list()
    tutor = await tutor_repo.get(id=meeting.tutor_id) if meeting.tutor_id else None
    tutor_items = [
        (
            index,
            {
                "id": tutor_item.id,
                "display": f"@{html.escape(tutor_item.username or '')} {html.escape(tutor_item.full_name)}",
            },
        )
        for index, tutor_item in enumerate(tutors)
    ]
    return {
        "title": html.escape(meeting.title),
        "description": html.escape(meeting.description) if meeting.description else None,
        "date": meeting.datetime_,
        "duration": meeting.duration_human,
        "tutor_username": html.escape(tutor.username) if tutor and tutor.username else None,
        "tutors": tutor_items,
    }


async def meeting_change_title_discipline_getter(dialog_manager: DialogManager, **kwargs):
    manager = extend_dialog(dialog_manager)
    meeting = await manager.state.get_meeting()
    title = await manager.state.get_value("title", None)
    discipline = await manager.state.get_value("discipline", None)
    if not title:
        title = meeting.title
    if not discipline:
        discipline = meeting.discipline
    else:
        discipline = Discipline.model_validate(discipline)
    return {
        "title": html.escape(title) if title else "Untitled",
        "discipline": discipline,
    }


async def meeting_change_date_room_getter(dialog_manager: DialogManager, **kwargs):
    manager = extend_dialog(dialog_manager)
    meeting = await manager.state.get_meeting()
    meeting_update = await manager.state.get_value("meeting_update", {})

    data = await user_status_getter(manager, **kwargs)
    is_admin: bool = data["is_admin"]
    tutor = await tutor_repo.get(id=meeting.tutor_id) if meeting.tutor_id else None
    is_assigned_tutor = bool(data["is_tutor"] and tutor and tutor.telegram_id == manager.chat.id)
    is_authorized = is_admin or is_assigned_tutor

    nothing_to_save = not meeting_update or len(meeting_update) == 0
    can_save_rightaway = (is_admin and not nothing_to_save) or (
        is_authorized and not nothing_to_save and meeting.status < MeetingStatus.ANNOUNCED
    )
    can_send_approve = (
        is_authorized
        and not nothing_to_save
        and meeting.status >= MeetingStatus.ANNOUNCED
        and meeting.status < MeetingStatus.CLOSED
        and not is_admin
    )

    if meeting_update:
        room = meeting_update["room"] if "room" in meeting_update else meeting.room
        date = datetime.fromisoformat(meeting_update["datetime"]) if "datetime" in meeting_update else meeting.datetime_
    else:
        room = meeting.room
        date = meeting.datetime_

    return {
        "date": date,
        "room": room if room else "N/A",
        "nothing_to_save": nothing_to_save,
        "can_save_rightaway": can_save_rightaway,
        "can_send_approve": can_send_approve,
    }
