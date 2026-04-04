from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager

from src.bot.constants import I18N_FORMAT_KEY
from src.bot.dialog_extension import extend_dialog
from src.bot.logging_ import log_info
from src.db.repositories import student_repo

from .states import GuideStates


async def _on_choose_language(query: CallbackQuery, manager: DialogManager, language: str):
    manager = extend_dialog(manager)
    async with manager.state.sync_self_student() as student:
        student.language = language
        await student_repo.update(student, ["language"])

    l10ns = manager.middleware_data.get("dialog_i18n_l10ns")
    default_lang = manager.middleware_data.get("dialog_i18n_default_lang", "en")
    if isinstance(l10ns, dict):
        l10n = l10ns.get(language) or l10ns.get(default_lang)
        if l10n is not None:
            manager.middleware_data[I18N_FORMAT_KEY] = l10n.format_value

    log_info("guide.language.selected", user_id=query.from_user.id, language=language)
    await manager.switch_to(GuideStates.init)


async def on_choose_language_en(query: CallbackQuery, _, manager: DialogManager):
    await _on_choose_language(query, manager, "en")


async def on_choose_language_ru(query: CallbackQuery, _, manager: DialogManager):
    await _on_choose_language(query, manager, "ru")


async def set_saw_guide_true(query: CallbackQuery, _, manager: DialogManager):
    manager = extend_dialog(manager)
    async with manager.state.sync_self_student() as student:
        student.saw_guide = True
        await student_repo.update(student, ["saw_guide"])
    log_info("guide.finished", user_id=query.from_user.id)
