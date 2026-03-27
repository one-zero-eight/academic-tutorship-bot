from src.bot.dialog_extension import extend_dialog
from src.bot.logging_ import log_info, log_warning
from src.bot.user_errors import *
from src.bot.utils import *
from src.db.repositories import discipline_repo

from .getters import *
from .states import *


async def on_language_select(query: CallbackQuery, widget, manager: DialogManager, item_id: str):
    manager = extend_dialog(manager)
    _ = manager.tr
    languages = await discipline_repo.get_languages()
    if int(item_id) >= len(languages):
        log_warning("discipline_picker.language.invalid", user_id=query.from_user.id, index=item_id)
        return await query.answer(_("Q_DISCIPLINE_PICKER_INVALID_LANGUAGE"), show_alert=True)
    chosen_language = languages[int(item_id)]
    multiple_choise = isinstance(manager.start_data, dict) and manager.start_data.get("multi", False)
    log_info(
        "discipline_picker.language.selected",
        user_id=query.from_user.id,
        language=chosen_language,
        multi_mode=multiple_choise,
    )
    await manager.state.update_data({"language": chosen_language})
    await manager.next()


async def on_year_select(query: CallbackQuery, widget, manager: DialogManager, item_id: str):
    manager = extend_dialog(manager)
    _ = manager.tr
    assert (language := await manager.state.get_value("language"))
    years = await discipline_repo.get_years(language)
    if int(item_id) >= len(years):
        log_warning("discipline_picker.year.invalid", user_id=query.from_user.id, index=item_id)
        return await query.answer(_("Q_DISCIPLINE_PICKER_INVALID_YEAR"), show_alert=True)
    chosen_year = years[int(item_id)]
    multiple_choise = isinstance(manager.start_data, dict) and manager.start_data.get("multi", False)
    log_info(
        "discipline_picker.year.selected",
        user_id=query.from_user.id,
        year=chosen_year,
        multi_mode=multiple_choise,
    )
    await manager.state.update_data({"year": chosen_year})
    if multiple_choise:
        await manager.switch_to(DisciplinePickerStates.discipline_multi)
    else:
        await manager.switch_to(DisciplinePickerStates.discipline)


async def on_discipline_select(query: CallbackQuery, widget, manager: DialogManager, item_id: str):
    manager = extend_dialog(manager)
    _ = manager.tr
    assert (language := await manager.state.get_value("language"))
    assert (year := await manager.state.get_value("year"))
    disciplines = await discipline_repo.get_list(language=language, year=year)
    if int(item_id) >= len(disciplines):
        log_warning("discipline_picker.discipline.invalid", user_id=query.from_user.id, index=item_id)
        return await query.answer(_("Q_DISCIPLINE_PICKER_INVALID_DISCIPLINE"), show_alert=True)
    chosen_discipline = disciplines[int(item_id)]
    log_info("discipline_picker.discipline.selected", user_id=query.from_user.id, discipline_id=chosen_discipline.id)
    await manager.state.update_data({"discipline": chosen_discipline.model_dump()})
    log_info("discipline_picker.discipline.done", user_id=query.from_user.id, discipline_id=chosen_discipline.id)
    await manager.done()


async def on_discipline_select_multi(query: CallbackQuery, widget, manager: DialogManager, item_id: str):
    manager = extend_dialog(manager)
    _ = manager.tr
    assert (language := await manager.state.get_value("language"))
    assert (year := await manager.state.get_value("year"))
    disciplines = await discipline_repo.get_list(language=language, year=year)
    if int(item_id) >= len(disciplines):
        log_warning("discipline_picker.discipline.invalid", user_id=query.from_user.id, index=item_id)
        return await query.answer(_("Q_DISCIPLINE_PICKER_INVALID_DISCIPLINE"), show_alert=True)
    chosen_discipline = disciplines[int(item_id)]
    selected_disciplines: list = await manager.state.get_value("selected_disciplines", [])
    selected_ids = [disc["id"] for disc in selected_disciplines]
    if chosen_discipline.id in selected_ids:
        del selected_disciplines[selected_ids.index(chosen_discipline.id)]
        selected = False
    else:
        selected_disciplines.append(chosen_discipline.model_dump())
        selected = True
    await manager.state.update_data({"selected_disciplines": selected_disciplines})
    log_info(
        "discipline_picker.discipline.toggled",
        user_id=query.from_user.id,
        discipline_id=chosen_discipline.id,
        selected=selected,
        selected_count=len(selected_disciplines),
    )
