from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode

from src.bot.dialog_extension import extend_dialog
from src.bot.user_errors import *
from src.bot.utils import *
from src.db.repositories import tutor_repo
from src.domain.models import Discipline

from .getters import *
from .states import *

# async def on_tutor_selected(query: CallbackQuery, widget: Any, manager: DialogManager, item_id: str):
#     manager = extend_dialog(manager)
#     tutor = await tutors_repo.get(id=int(item_id))
#     tutor_profile = await tutor_profiles_repo.get(id=int(item_id))
#     await manager.state.set_tutor(tutor)
#     await manager.state.set_tutor_profile(tutor_profile)
#     await manager.switch_to(TutorProfileStates.profile_after_list)


async def on_open_disciplines(query: CallbackQuery, widget, manager: DialogManager):
    manager = extend_dialog(manager)
    assert (tutor := await manager.state.get_self_tutor())
    disciplines = await tutor_repo.get_disciplines(tutor.id)
    selected_disciplines = [disc.model_dump() for disc in disciplines]
    await manager.state.update_data({"selected_disciplines": selected_disciplines})


async def on_submit_disciplines(query: CallbackQuery, widget, manager: DialogManager):
    manager = extend_dialog(manager)
    assert (tutor := await manager.state.get_self_tutor())
    selected_disciplines = await manager.state.get_value("selected_disciplines", [])
    disciplines = [Discipline(**disc) for disc in selected_disciplines]
    await tutor_repo.set_disciplines(tutor.id, disciplines)


async def get_profile_name(message: Message, _, manager: DialogManager):
    manager = extend_dialog(manager)
    await manager.clear_messages()
    await message.delete()
    if not message.text:
        return await manager.answer_and_retry("There is no text in your message")
    if len(message.text.strip()) > 128:
        return await manager.answer_and_retry("Your message must be under 128 simbols long")
    async with manager.state.sync_self_tutor() as tutor:
        tutor.profile_name = message.text.strip()
        await tutor_repo.update(tutor, ["profile_name"])
    await manager.switch_to(state=TutorProfileStates.profile_control, show_mode=ShowMode.DELETE_AND_SEND)


async def get_about_text(message: Message, _, manager: DialogManager):
    manager = extend_dialog(manager)
    await manager.clear_messages()
    await message.delete()
    if not message.text:
        return await manager.answer_and_retry("There is no text in your message")
    if len(message.text.strip()) > 256:
        return await manager.answer_and_retry("Your message must be under 256 simbols long")
    async with manager.state.sync_self_tutor() as tutor:
        tutor.about = message.text.strip()
        await tutor_repo.update(tutor, ["about"])
    await manager.switch_to(state=TutorProfileStates.profile_control, show_mode=ShowMode.DELETE_AND_SEND)


# async def get_profile_photo(message: Message, _, manager: DialogManager):
#     manager = extend_dialog(manager)
#     await manager.clear_messages()
#     await message.delete()
#     if not message.photo:
#         return await manager.answer_and_retry("You've send no photo")
#     async with manager.state.sync_tutor() as tutor:
#         await tutor.
#     await manager.switch_to(state=TutorProfileStates.profile_control, show_mode=ShowMode.DELETE_AND_SEND)


async def open_tutor_profile(query: CallbackQuery, button: Button, manager: DialogManager):
    manager = extend_dialog(manager)
    meeting = await manager.state.get_meeting()
    tutor = await tutor_repo.get(id=meeting.tutor_id)
    if tutor.profile_name is None:
        return await query.answer("Tutor hasn't set up their profile yet", show_alert=True)
    await manager.state.set_tutor(tutor)
    await manager.start(state=TutorProfileStates.profile)
