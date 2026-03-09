from aiogram_dialog import DialogManager

from src.bot.dialog_extension import extend_dialog
from src.bot.dialogs.meetings.getters import meeting_info_getter
from src.bot.filters import *
from src.bot.utils import *
from src.db.repositories import tutor_repo


async def meeting_info_with_tutors_getter(dialog_manager: DialogManager, **kwargs):
    manager = extend_dialog(dialog_manager)
    meeting = await manager.state.get_meeting()
    tutors = await tutor_repo.get_list()
    tutor = await tutor_repo.get(id=meeting.tutor_id) if meeting.tutor_id else None
    return {
        "title": meeting.title,
        "description": meeting.description,
        "date": meeting.datetime_,
        "duration": meeting.duration_human,
        "tutor_username": tutor.username if tutor else None,
        "tutors": list(enumerate(tutors)),
    }


__all__ = ["meeting_info_getter", "meeting_info_with_tutors_getter"]
