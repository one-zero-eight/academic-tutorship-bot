from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager

from src.bot.dialog_extension import extend_dialog
from src.bot.logging_ import log_error, log_info
from src.db.repositories import student_repo

NOTIFICATIONS_ON = "Thanks! Don't forget to launch @"
NOTIFICATIONS_OFF = "We won't bother you with notifications anymore"


async def on_toggle_notifications(query: CallbackQuery, _, manager: DialogManager):
    manager = extend_dialog(manager)
    try:
        async with manager.state.sync_self_student() as self_student:
            s = self_student.settings
            log_info(
                "student.notifications.toggle.requested",
                user_id=query.from_user.id,
                current_value=s.receive_notifications,
            )
            s.receive_notifications = not s.receive_notifications
            await student_repo.update(self_student, ["receive_notifications"])
            log_info(
                "student.notifications.toggle.succeeded",
                user_id=query.from_user.id,
                new_value=s.receive_notifications,
            )
    except Exception as e:
        log_error("student.notifications.toggle.failed", user_id=query.from_user.id, reason=str(e))
        raise
    await query.answer()
    await manager.switch_to_current()


async def on_open_disciplines(query: CallbackQuery, widget, manager: DialogManager):
    manager = extend_dialog(manager)
    try:
        assert (self_student := await manager.state.get_self_student())
        log_info("student.disciplines.open.requested", user_id=query.from_user.id)
        disciplines = await student_repo.get_relevant_disciplines(self_student.telegram_id)
        selected_disciplines = [disc.model_dump() for disc in disciplines]
        await manager.state.update_data({"selected_disciplines": selected_disciplines})
        log_info(
            "student.disciplines.open.succeeded", user_id=query.from_user.id, selected_count=len(selected_disciplines)
        )
    except Exception as e:
        log_error("student.disciplines.open.failed", user_id=query.from_user.id, reason=str(e))
        raise


async def on_submit_disciplines(query: CallbackQuery, widget, manager: DialogManager):
    manager = extend_dialog(manager)
    try:
        assert (self_student := await manager.state.get_self_student())
        selected_disciplines = await manager.state.get_value("selected_disciplines", [])
        discipline_ids = [disc["id"] for disc in selected_disciplines]
        log_info("student.disciplines.submit.requested", user_id=query.from_user.id, selected_count=len(discipline_ids))
        await student_repo.set_relevant_disciplines(self_student.telegram_id, discipline_ids)
        log_info("student.disciplines.submit.succeeded", user_id=query.from_user.id, selected_count=len(discipline_ids))
    except Exception as e:
        log_error("student.disciplines.submit.failed", user_id=query.from_user.id, reason=str(e))
        raise
