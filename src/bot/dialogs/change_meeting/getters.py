from aiogram_dialog import DialogManager

from src.bot.dialog_extension import extend_dialog
from src.bot.dialogs.meetings.getters import meeting_info_getter
from src.bot.dto import *
from src.bot.filters import *
from src.bot.utils import *
from src.db.repositories import tutors_repo


async def meeting_info_with_tutors_getter(dialog_manager: DialogManager, **kwargs):
    manager = extend_dialog(dialog_manager)
    meeting = await manager.state.get_meeting()
    tutors = await tutors_repo.list()
    return {
        "title": meeting.title,
        "description": meeting.description,
        "date": meeting.date_human,
        "duration": meeting.duration_human,
        "tutor_username": meeting.tutor.username if meeting.tutor else None,
        "tutors": list(enumerate(tutors)),
    }


__all__ = ["meeting_info_getter", "meeting_info_with_tutors_getter"]
