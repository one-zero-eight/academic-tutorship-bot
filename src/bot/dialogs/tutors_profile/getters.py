from aiogram_dialog import DialogManager

from src.bot.dto import *
from src.bot.filters import *
from src.bot.utils import *
from src.db.repositories import tutors_repo


async def tutors_list_getter(dialog_manager: DialogManager, **kwargs):
    tutors = await tutors_repo.list()
    return {
        "tutors": list(enumerate(tutors)),
    }


async def tutor_profile_getter(dialog_manager: DialogManager, **kwargs):
    manager = extend_dialog(dialog_manager)
    tutor_profile = await manager.state.get_tutor_profile()
    return {
        "full_name": tutor_profile.full_name,
        "username": tutor_profile.username,
        "discipline": tutor_profile.discipline,
        "about": tutor_profile.about,
        "photo_id": tutor_profile.photo_id,
    }
