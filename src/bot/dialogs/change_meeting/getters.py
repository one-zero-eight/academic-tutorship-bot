import html

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


__all__ = ["meeting_info_getter", "meeting_info_with_tutors_getter"]
