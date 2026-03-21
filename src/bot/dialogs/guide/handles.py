from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager

from src.bot.dialog_extension import extend_dialog
from src.bot.logging_ import log_info
from src.db.repositories import student_repo


async def set_saw_guide_true(query: CallbackQuery, _, manager: DialogManager):
    manager = extend_dialog(manager)
    async with manager.state.sync_self_student() as student:
        student.saw_guide = True
        await student_repo.update(student, ["saw_guide"])
    log_info("guide.finished", user_id=query.from_user.id)
