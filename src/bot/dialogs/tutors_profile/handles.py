from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager

from src.bot.dialog_extension import extend_dialog
from src.bot.user_errors import *
from src.bot.utils import *
from src.db.repositories import tutor_profiles_repo, tutors_repo

from .getters import *
from .states import *


async def on_tutor_selected(query: CallbackQuery, widget: Any, manager: DialogManager, item_id: str):
    manager = extend_dialog(manager)
    tutor = await tutors_repo.get(id=int(item_id))
    tutor_profile = await tutor_profiles_repo.get(id=int(item_id))
    await manager.state.set_tutor(tutor)
    await manager.state.set_tutor_profile(tutor_profile)
    await manager.switch_to(TutorProfileStates.profile_after_list)
