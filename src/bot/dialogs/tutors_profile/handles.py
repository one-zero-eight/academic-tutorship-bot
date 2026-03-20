from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode

from src.bot.dialog_extension import extend_dialog
from src.bot.logging_ import log_error, log_info, log_warning
from src.bot.user_errors import *
from src.bot.utils import *
from src.db.repositories import tutor_repo
from src.domain.models import Discipline

from .getters import *
from .states import *


async def on_tutor_selected(query: CallbackQuery, _, manager: DialogManager, item_id: str):
    manager = extend_dialog(manager)
    log_info("tutor_profile.select.requested", user_id=query.from_user.id, tutor_id=item_id)
    try:
        tutor = await tutor_repo.get(id=int(item_id))
    except LookupError:
        log_warning("tutor_profile.select.not_found", user_id=query.from_user.id, tutor_id=item_id)
        return await query.answer("Tutor not found", show_alert=True)
    await manager.state.set_tutor(tutor)
    log_info("tutor_profile.select.succeeded", user_id=query.from_user.id, tutor_id=tutor.id)
    await manager.switch_to(TutorProfileStates.profile_after_list)


async def on_open_disciplines(query: CallbackQuery, widget, manager: DialogManager):
    manager = extend_dialog(manager)
    try:
        assert (tutor := await manager.state.get_self_tutor())
        disciplines = await tutor_repo.get_disciplines(tutor.id)
        selected_disciplines = [disc.model_dump() for disc in disciplines]
        await manager.state.update_data({"selected_disciplines": selected_disciplines})
        log_info(
            "tutor_profile.disciplines.opened", user_id=query.from_user.id, selected_count=len(selected_disciplines)
        )
    except Exception as e:
        log_error("tutor_profile.disciplines.open.failed", user_id=query.from_user.id, reason=str(e))
        raise


async def on_submit_disciplines(query: CallbackQuery, widget, manager: DialogManager):
    manager = extend_dialog(manager)
    try:
        assert (tutor := await manager.state.get_self_tutor())
        selected_disciplines = await manager.state.get_value("selected_disciplines", [])
        disciplines = [Discipline(**disc) for disc in selected_disciplines]
        log_info(
            "tutor_profile.disciplines.submit.requested", user_id=query.from_user.id, selected_count=len(disciplines)
        )
        await tutor_repo.set_disciplines(tutor.id, disciplines)
        log_info(
            "tutor_profile.disciplines.submit.succeeded", user_id=query.from_user.id, selected_count=len(disciplines)
        )
    except Exception as e:
        log_error("tutor_profile.disciplines.submit.failed", user_id=query.from_user.id, reason=str(e))
        raise


async def get_profile_name(message: Message, _, manager: DialogManager):
    manager = extend_dialog(manager)
    await manager.clear_messages()
    await message.delete()
    if not message.text:
        log_warning("tutor_profile.name.update.invalid", user_id=message.chat.id, reason="empty")
        return await manager.answer_and_retry("There is no text in your message")
    if len(message.text.strip()) > 128:
        log_warning("tutor_profile.name.update.invalid", user_id=message.chat.id, reason="too_long")
        return await manager.answer_and_retry("Your message must be under 128 simbols long")
    try:
        async with manager.state.sync_self_tutor() as tutor:
            log_info("tutor_profile.name.update.requested", user_id=message.chat.id)
            tutor.profile_name = message.text.strip()
            await tutor_repo.update(tutor, ["profile_name"])
    except Exception as e:
        log_error("tutor_profile.name.update.failed", user_id=message.chat.id, reason=str(e))
        raise
    log_info("tutor_profile.name.update.succeeded", user_id=message.chat.id)
    await manager.switch_to(state=TutorProfileStates.profile_control, show_mode=ShowMode.DELETE_AND_SEND)


async def get_about_text(message: Message, _, manager: DialogManager):
    manager = extend_dialog(manager)
    await manager.clear_messages()
    await message.delete()
    if not message.text:
        log_warning("tutor_profile.about.update.invalid", user_id=message.chat.id, reason="empty")
        return await manager.answer_and_retry("There is no text in your message")
    if len(message.text.strip()) > 256:
        log_warning("tutor_profile.about.update.invalid", user_id=message.chat.id, reason="too_long")
        return await manager.answer_and_retry("Your message must be under 256 simbols long")
    try:
        async with manager.state.sync_self_tutor() as tutor:
            log_info("tutor_profile.about.update.requested", user_id=message.chat.id)
            tutor.about = message.text.strip()
            await tutor_repo.update(tutor, ["about"])
    except Exception as e:
        log_error("tutor_profile.about.update.failed", user_id=message.chat.id, reason=str(e))
        raise
    log_info("tutor_profile.about.update.succeeded", user_id=message.chat.id)
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
    log_info("tutor_profile.open.requested", user_id=query.from_user.id, meeting_id=meeting.id)
    tutor = await tutor_repo.get(id=meeting.tutor_id)
    if tutor.profile_name is None:
        log_warning("tutor_profile.open.profile_not_ready", user_id=query.from_user.id, tutor_id=tutor.id)
        return await query.answer("Tutor hasn't set up their profile yet", show_alert=True)
    await manager.state.set_tutor(tutor)
    log_info("tutor_profile.open.succeeded", user_id=query.from_user.id, tutor_id=tutor.id)
    await manager.start(state=TutorProfileStates.profile)
