from aiogram_dialog import DialogManager

from src.bot.filters import *
from src.bot.utils import *
from src.db.repositories import tutor_repo


async def tutors_list_getter(dialog_manager: DialogManager, **kwargs):
    tutors = await tutor_repo.get_list()
    return {
        "tutors": list(enumerate(tutors)),
    }


async def tutor_profile_getter(dialog_manager: DialogManager, **kwargs):
    manager = extend_dialog(dialog_manager)
    tutor = await manager.state.get_tutor()
    disciplines = await tutor_repo.get_disciplines(tutor.id)
    return {
        "profile_name": tutor.profile_name,
        "username": tutor.username,
        "disciplines": disciplines,
        "about": tutor.about,
        "photo": tutor.photo,
    }


async def self_tutor_profile_getter(dialog_manager: DialogManager, **kwargs):
    manager = extend_dialog(dialog_manager)
    tutor = await manager.state.get_self_tutor()
    disciplines = await tutor_repo.get_disciplines(tutor.id)
    return {
        "profile_name": tutor.profile_name,
        "username": tutor.username,
        "disciplines": disciplines,
        "about": tutor.about,
        "photo": tutor.photo,
    }


async def selected_disciplines_getter(dialog_manager: DialogManager, **kwargs):
    manager = extend_dialog(dialog_manager)
    selected_disciplines = await manager.state.get_value("selected_disciplines", [])
    return {"selected_disciplines": selected_disciplines}
