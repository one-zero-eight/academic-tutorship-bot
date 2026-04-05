import html

from aiogram_dialog import DialogManager

from src.bot.filters import *
from src.bot.utils import *
from src.db.repositories import tutor_repo


async def tutors_list_getter(dialog_manager: DialogManager, **kwargs):
    tutors = await tutor_repo.get_list(with_profiles_only=True)
    tutor_items = [
        (
            index,
            {
                "id": tutor.id,
                "display": f"{html.escape(tutor.profile_name or '')} @{html.escape(tutor.username or '')}",
            },
        )
        for index, tutor in enumerate(tutors)
    ]
    return {
        "tutors": tutor_items,
    }


async def tutor_profile_getter(dialog_manager: DialogManager, **kwargs):
    manager = extend_dialog(dialog_manager)
    tutor = await manager.state.get_tutor()
    disciplines = await tutor_repo.get_disciplines(tutor.id)
    return {
        "profile_name": html.escape(tutor.profile_name or ""),
        "username": html.escape(tutor.username or ""),
        "disciplines": disciplines,
        "about": html.escape(tutor.about) if tutor.about else None,
        "photo": tutor.photo,
    }


async def self_tutor_profile_getter(dialog_manager: DialogManager, **kwargs):
    manager = extend_dialog(dialog_manager)
    tutor = await manager.state.get_self_tutor()
    disciplines = await tutor_repo.get_disciplines(tutor.id)
    return {
        "profile_name": html.escape(tutor.profile_name or ""),
        "username": html.escape(tutor.username or ""),
        "disciplines": disciplines,
        "about": html.escape(tutor.about) if tutor.about else None,
        "photo": tutor.photo,
    }


async def selected_disciplines_getter(dialog_manager: DialogManager, **kwargs):
    manager = extend_dialog(dialog_manager)
    selected_disciplines = await manager.state.get_value("selected_disciplines", [])
    selected_disciplines_safe = [
        {
            **discipline,
            "display": (
                f"- [{html.escape(str(discipline['language']))} {discipline['year']}y] "
                f"{html.escape(str(discipline['name']))}"
            ),
        }
        for discipline in selected_disciplines
    ]
    return {"selected_disciplines": selected_disciplines_safe}
