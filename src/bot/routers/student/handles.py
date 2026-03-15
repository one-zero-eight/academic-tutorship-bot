from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager

from src.bot.dialog_extension import extend_dialog
from src.db.repositories import student_repo

NOTIFICATIONS_ON = "Thanks! Don't forget to launch @"
NOTIFICATIONS_OFF = "We won't bother you with notifications anymore"


async def on_toggle_notifications(query: CallbackQuery, _, manager: DialogManager):
    manager = extend_dialog(manager)
    async with manager.state.sync_self_student() as self_student:
        s = self_student.settings
        s.receive_notifications = not s.receive_notifications
        await student_repo.update(self_student, ["receive_notifications"])
    await query.answer()
    await manager.switch_to_current()


async def on_open_disciplines(query: CallbackQuery, widget, manager: DialogManager):
    manager = extend_dialog(manager)
    assert (self_student := await manager.state.get_self_student())
    disciplines = await student_repo.get_relevant_disciplines(self_student.telegram_id)
    selected_disciplines = [disc.model_dump() for disc in disciplines]
    await manager.state.update_data({"selected_disciplines": selected_disciplines})


async def on_submit_disciplines(query: CallbackQuery, widget, manager: DialogManager):
    manager = extend_dialog(manager)
    assert (self_student := await manager.state.get_self_student())
    selected_disciplines = await manager.state.get_value("selected_disciplines", [])
    discipline_ids = [disc["id"] for disc in selected_disciplines]
    await student_repo.set_relevant_disciplines(self_student.telegram_id, discipline_ids)
