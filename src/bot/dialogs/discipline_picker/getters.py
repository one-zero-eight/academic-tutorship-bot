from aiogram_dialog import DialogManager

from src.bot.dialog_extension import extend_dialog
from src.db.repositories import discipline_repo


async def languages_getter(dialog_manager: DialogManager, **kwargs):
    languages = await discipline_repo.get_languages()
    multiple_choise = isinstance(dialog_manager.start_data, dict) and dialog_manager.start_data.get("multi", False)
    return {
        "languages": list(enumerate(languages)),
        "multi": multiple_choise,
        "not_multi": not multiple_choise,
    }


async def years_getter(dialog_manager: DialogManager, **kwargs):
    manager = extend_dialog(dialog_manager)
    language = await manager.state.get_value("language")
    assert language
    years = await discipline_repo.get_years(language)
    multiple_choise = isinstance(dialog_manager.start_data, dict) and dialog_manager.start_data.get("multi", False)
    return {
        "years": list(enumerate(years)),
        "multi": multiple_choise,
        "not_multi": not multiple_choise,
    }


async def disciplines_getter(dialog_manager: DialogManager, **kwargs):
    manager = extend_dialog(dialog_manager)
    assert (language := await manager.state.get_value("language"))
    assert (year := await manager.state.get_value("year"))
    disciplines = await discipline_repo.get_list(language=language, year=year)
    return {"disciplines": list(enumerate(disciplines))}


async def disciplines_multi_getter(dialog_manager: DialogManager, **kwargs):
    manager = extend_dialog(dialog_manager)
    assert (language := await manager.state.get_value("language"))
    assert (year := await manager.state.get_value("year"))
    selected_disciplines = await manager.state.get_value("selected_disciplines", [])
    selected_ids = [disc["id"] for disc in selected_disciplines]
    disciplines = await discipline_repo.get_list(language=language, year=year)
    disciplines_multi = []
    for id, disc in enumerate(disciplines):
        status = "✅" if disc.id in selected_ids else "⏺️"
        disciplines_multi.append((id, disc, status))
    return {"disciplines_multi": disciplines_multi}
