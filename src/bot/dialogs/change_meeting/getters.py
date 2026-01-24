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

    tutors = await tutors_repo.list()

    return {
        "title": meeting.title,
        "description": meeting.description,
        "date": meeting.date_human,
        "duration": meeting.duration_human,
        "tutor_username": meeting.tutor.username if meeting.tutor else None,
        "tutors": list(enumerate(tutors)),
    }
