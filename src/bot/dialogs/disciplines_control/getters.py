from aiogram_dialog import DialogManager

from src.db.repositories import discipline_repo


async def disciplines_getter(dialog_manager: DialogManager, **kwargs):
    disciplines = await discipline_repo.get_full_list()
    disciplines.sort(key=lambda d: (d.language, d.year, d.semester, d.id))
    return {"disciplines": disciplines}
