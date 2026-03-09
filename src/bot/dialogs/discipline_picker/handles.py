from src.bot.dialog_extension import extend_dialog
from src.bot.user_errors import *
from src.bot.utils import *
from src.db.repositories import discipline_repo

from .getters import *
from .states import *


async def on_language_select(query: CallbackQuery, widget, manager: DialogManager, item_id: str):
    manager = extend_dialog(manager)
    languages = await discipline_repo.get_languages()
    chosen_language = languages[int(item_id)]
    await manager.state.update_data({"language": chosen_language})
    await manager.next()


async def on_year_select(query: CallbackQuery, widget, manager: DialogManager, item_id: str):
    manager = extend_dialog(manager)
    assert (language := await manager.state.get_value("language"))
    years = await discipline_repo.get_years(language)
    chosen_year = years[int(item_id)]
    await manager.state.update_data({"year": chosen_year})
    multiple_choise = isinstance(manager.start_data, dict) and manager.start_data.get("multi", False)
    if multiple_choise:
        await manager.switch_to(DisciplinePickerStates.discipline_multi)
    else:
        await manager.switch_to(DisciplinePickerStates.discipline)


async def on_discipline_select(query: CallbackQuery, widget, manager: DialogManager, item_id: str):
    manager = extend_dialog(manager)
    assert (language := await manager.state.get_value("language"))
    assert (year := await manager.state.get_value("year"))
    disciplines = await discipline_repo.get_list(language=language, year=year)
    chosen_discipline = disciplines[int(item_id)]
    await manager.state.update_data({"discipline": chosen_discipline.model_dump()})
    await manager.done()


async def on_discipline_select_multi(query: CallbackQuery, widget, manager: DialogManager, item_id: str):
    manager = extend_dialog(manager)
    assert (language := await manager.state.get_value("language"))
    assert (year := await manager.state.get_value("year"))
    disciplines = await discipline_repo.get_list(language=language, year=year)
    chosen_discipline = disciplines[int(item_id)]
    selected_disciplines: list = await manager.state.get_value("selected_disciplines", [])
    selected_ids = [disc["id"] for disc in selected_disciplines]
    if chosen_discipline.id in selected_ids:
        del selected_disciplines[selected_ids.index(chosen_discipline.id)]
    else:
        selected_disciplines.append(chosen_discipline.model_dump())
    await manager.state.update_data({"selected_disciplines": selected_disciplines})
