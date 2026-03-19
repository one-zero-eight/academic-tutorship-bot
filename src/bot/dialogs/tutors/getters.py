import html

from aiogram_dialog import DialogManager

from src.bot.dialog_extension import extend_dialog
from src.bot.filters import *
from src.bot.utils import *
from src.db.repositories import tutor_repo


async def tutors_list_getter(dialog_manager: DialogManager, **kwargs):
    tutors = await tutor_repo.get_list()
    tutor_items = [
        (
            index,
            {
                "id": tutor.id,
                "display": f"@{html.escape(tutor.username or '')} {html.escape(tutor.full_name)}",
            },
        )
        for index, tutor in enumerate(tutors)
    ]
    return {
        "tutors": tutor_items,
    }


async def tutor_info_getter(dialog_manager: DialogManager, **kwargs):
    manager = extend_dialog(dialog_manager)
    tutor = await manager.state.get_tutor()
    return {
        "id": tutor.id,
        "telegram_id": tutor.telegram_id,
        "username": html.escape(tutor.username or ""),
        "full_name": html.escape(tutor.full_name),
        "profile_set": tutor.profile_name is not None,
        "own_tutor_profile": tutor.telegram_id == manager.chat.id,
        "other_tutor_profile": tutor.telegram_id != manager.chat.id,
    }
