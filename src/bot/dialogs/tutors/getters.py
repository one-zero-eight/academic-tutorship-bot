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


async def tutor_info_getter(dialog_manager: DialogManager, **kwargs):
    state = get_state(dialog_manager)
    tutor = dto_to_tutor(await state.get_value("tutor"))
    if not tutor:
        raise ValueError("No Tutor in tutor_info_getter")
    return {
        "id": tutor.id,
        "tg_id": tutor.tg_id,
        "username": tutor.username,
        "full_name": tutor.full_name,
    }
