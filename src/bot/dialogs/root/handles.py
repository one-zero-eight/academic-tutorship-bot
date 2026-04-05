from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager

from src.bot.constants import I18N_FORMAT_KEY
from src.bot.dialog_extension import extend_dialog
from src.bot.logging_ import log_error, log_info, log_warning
from src.db.repositories import student_repo
from src.domain.models import NotificationBotStatus
from src.notifications import notification_manager


async def on_toggle_language(query: CallbackQuery, _, manager: DialogManager):
    manager = extend_dialog(manager)
    try:
        self_student = await manager.state.get_self_student()
        old_language = self_student.language if self_student.language in {"en", "ru"} else "en"
        new_language = "ru" if old_language == "en" else "en"
        log_info(
            "student.language.toggle.requested",
            user_id=query.from_user.id,
            old_language=old_language,
            new_language=new_language,
        )

        self_student.language = new_language
        await student_repo.update(self_student, ["language"])
        await manager.state.set_self_student(self_student)

        # Rebind formatter in current callback context so the same render cycle uses the new language.
        l10ns = manager.middleware_data.get("dialog_i18n_l10ns")
        default_lang = manager.middleware_data.get("dialog_i18n_default_lang", "en")
        if isinstance(l10ns, dict):
            l10n = l10ns.get(new_language) or l10ns.get(default_lang)
            if l10n is not None:
                manager.middleware_data[I18N_FORMAT_KEY] = l10n.format_value

        _ = manager.tr

        await query.answer(_("Q_SETTINGS_LANGUAGE_CHANGED"))
        log_info(
            "student.language.toggle.succeeded",
            user_id=query.from_user.id,
            language=new_language,
        )
    except Exception as e:
        log_error("student.language.toggle.failed", user_id=query.from_user.id, reason=str(e))
        raise
    await manager.switch_to_current()


async def on_toggle_notifications(query: CallbackQuery, _, manager: DialogManager):
    manager = extend_dialog(manager)
    _ = manager.tr
    try:
        self_student = await manager.state.get_self_student()
        s = self_student.settings
        log_info(
            "student.notifications.toggle.requested",
            user_id=query.from_user.id,
            current_value=s.receive_notifications,
        )
        s.receive_notifications = not s.receive_notifications
        await student_repo.update(self_student, ["receive_notifications"])
        await notification_manager.send_receive_notification_toggled(self_student.id, s.receive_notifications)
        self_student = await student_repo.get(self_student.telegram_id)  # check if notification really sent

        if self_student.notification_bot_status != NotificationBotStatus.ACTIVATED:
            # NOTE: we don't care if user deactivates notifications and blocks bot
            if s.receive_notifications:
                raise PermissionError("Notification bot is not activated")

        await student_repo.update(self_student, ["receive_notifications"])
        await query.answer(_("Q_SETTINGS_NOTIF_ON") if s.receive_notifications else _("Q_SETTINGS_NOTIF_OFF"))
        await manager.state.set_self_student(self_student)
        log_info(
            "student.notifications.toggle.succeeded",
            user_id=query.from_user.id,
            new_value=s.receive_notifications,
        )
    except PermissionError:
        log_warning(
            "student.notifications.toggle.permission_denied",
            user_id=query.from_user.id,
        )
        self_student.settings.receive_notifications = False
        await student_repo.update(self_student, ["receive_notifications"])
        await query.answer(_("Q_SETTINGS_NOTIF_BOT_NOT_ACTIVATED"))
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
