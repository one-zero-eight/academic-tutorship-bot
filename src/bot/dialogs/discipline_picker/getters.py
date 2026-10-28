import html

from aiogram_dialog import DialogManager

from src.bot.dialog_extension import extend_dialog
from src.db.repositories import discipline_repo


async def languages_getter(dialog_manager: DialogManager, **kwargs):
    languages = await discipline_repo.get_languages()
    multiple_choise = isinstance(dialog_manager.start_data, dict) and dialog_manager.start_data.get("multi", False)
    language_items = [(index, html.escape(str(language))) for index, language in enumerate(languages)]
    return {
        "languages": language_items,
        "multi": multiple_choise,
        "not_multi": not multiple_choise,
    }


async def years_getter(dialog_manager: DialogManager, **kwargs):
    manager = extend_dialog(dialog_manager)
    language = await manager.state.get_value("language")
    assert language
    years = await discipline_repo.get_years(language)
    multiple_choise = isinstance(dialog_manager.start_data, dict) and dialog_manager.start_data.get("multi", False)
    year_items = [(index, html.escape(str(year))) for index, year in enumerate(years)]
    return {
        "years": year_items,
        "multi": multiple_choise,
        "not_multi": not multiple_choise,
    }


async def semesters_getter(dialog_manager: DialogManager, **kwargs):
    manager = extend_dialog(dialog_manager)
    assert (language := await manager.state.get_value("language"))
    assert (year := await manager.state.get_value("year"))
    semesters = await discipline_repo.get_semesters(language=language, year=year)
    multiple_choise = isinstance(dialog_manager.start_data, dict) and dialog_manager.start_data.get("multi", False)
    semester_items = [(index, html.escape(str(semester))) for index, semester in enumerate(semesters)]
    return {
        "semesters": semester_items,
        "multi": multiple_choise,
        "not_multi": not multiple_choise,
    }


async def disciplines_getter(dialog_manager: DialogManager, **kwargs):
    manager = extend_dialog(dialog_manager)
    assert (language := await manager.state.get_value("language"))
    assert (year := await manager.state.get_value("year"))
    assert (semester := await manager.state.get_value("semester"))
    disciplines = await discipline_repo.get_list(language=language, year=year, semester=semester)
    discipline_items = [
        (
            index,
            {
                "id": discipline.id,
                "display": discipline.name,
            },
        )
        for index, discipline in enumerate(disciplines)
    ]
    return {"disciplines": discipline_items}


async def disciplines_multi_getter(dialog_manager: DialogManager, **kwargs):
    manager = extend_dialog(dialog_manager)
    assert (language := await manager.state.get_value("language"))
    assert (year := await manager.state.get_value("year"))
    assert (semester := await manager.state.get_value("semester"))
    selected_disciplines = await manager.state.get_value("selected_disciplines", [])
    selected_ids = [disc["id"] for disc in selected_disciplines]
    disciplines = await discipline_repo.get_list(language=language, year=year, semester=semester)
    disciplines_multi = []
    for id, disc in enumerate(disciplines):
        status = "✅" if disc.id in selected_ids else "⏺️"
        disciplines_multi.append((id, {"id": disc.id, "display": disc.name}, status))
    return {"disciplines_multi": disciplines_multi}


async def selected_disciplines_getter(dialog_manager: DialogManager, **kwargs):
    manager = extend_dialog(dialog_manager)
    selected_disciplines = await manager.state.get_value("selected_disciplines", [])
    something_chosen = len(selected_disciplines) > 0
    return {
        "selected_disciplines": selected_disciplines,
        "something_chosen": something_chosen,
        "nothing_chosen": not something_chosen,
    }
