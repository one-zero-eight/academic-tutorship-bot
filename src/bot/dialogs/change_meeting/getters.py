from datetime import datetime

from aiogram_dialog import DialogManager

from src.bot.dto import *
from src.bot.filters import *
from src.bot.utils import *
from src.db.repositories import tutors_repo


async def meeting_info_with_tutors_getter(dialog_manager: DialogManager, **kwargs):
    state = get_state(dialog_manager)
    meeting = dto_to_meeting(await state.get_value("meeting"))

    if not meeting:
        raise ValueError("No Meeting in meeting_info_getter")

    date_to_str = lambda x: datetime.fromtimestamp(x).strftime("%d.%m.%Y")  # noqa E731
    duration_to_str = lambda x: f"{x // 3600:02d}:{(x % 3600) // 60:02d}"  # noqa E731
    tutors = await tutors_repo.list()

    return {
        "title": meeting.title,
        "description": meeting.description,
        "date": date_to_str(meeting.date) if meeting.date else "--.--.----",
        "duration": duration_to_str(meeting.duration) if meeting.duration else "--:--",
        "tutor_username": meeting.tutor.username if meeting.tutor else None,
        "tutors": list(enumerate(tutors)),
    }


async def meeting_info_getter(dialog_manager: DialogManager, **kwargs):
    state = get_state(dialog_manager)
    meeting = dto_to_meeting(await state.get_value("meeting"))

    if not meeting:
        raise ValueError("No Meeting in meeting_info_getter")

    date_to_str = lambda x: datetime.fromtimestamp(x).strftime("%d.%m.%Y")  # noqa E731
    duration_to_str = lambda x: f"{x // 3600:02d}:{(x % 3600) // 60:02d}"  # noqa E731

    return {
        "title": meeting.title,
        "description": meeting.description,
        "date": date_to_str(meeting.date) if meeting.date else "--.--.----",
        "duration": duration_to_str(meeting.duration) if meeting.duration else "--:--",
        "tutor_username": meeting.tutor.username if meeting.tutor else None,
    }
