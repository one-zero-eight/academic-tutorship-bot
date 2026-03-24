from typing import Literal

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Button

from src.bot.dialog_extension import extend_dialog
from src.bot.logging_ import log_error, log_info, log_warning
from src.bot.user_errors import *
from src.bot.utils import *
from src.db.repositories import meeting_repo
from src.domain.models import MeetingStatus

from .logic import *
from .states import *


async def on_meeting_selected(query: CallbackQuery, meeting, manager: DialogManager, item_id: str):
    manager = extend_dialog(manager)
    log_info("meeting.select.requested", user_id=query.from_user.id, meeting_id=item_id)
    try:
        meeting = await meeting_repo.get(int(item_id))
    except LookupError:
        log_warning("meeting.select.not_found", user_id=query.from_user.id, meeting_id=item_id)
        return await query.answer("Meeting not found", show_alert=True)
    await manager.state.set_meeting(meeting)
    log_info("meeting.select.succeeded", user_id=query.from_user.id, meeting_id=meeting.id)
    await manager.switch_to(MeetingStates.info)


def open_meetings_list_of_type(type: Literal["created", "approving", "announced", "closed"]):
    """Higher order function, returns Awaitable that opens specified meetings list"""

    async def open_meetings_list(query: CallbackQuery, _, manager: DialogManager):
        manager = extend_dialog(manager)
        log_info("meeting.list.requested", user_id=query.from_user.id, meetings_type=type)
        await manager.state.update_data({"meetings_type": type})
        log_info("meeting.list.opened", user_id=query.from_user.id, meetings_type=type)
        await manager.switch_to(MeetingStates.list)

    return open_meetings_list


async def get_new_title(message: Message, _, manager: DialogManager):
    manager = extend_dialog(manager)
    await manager.clear_messages()
    await message.delete()
    if not message.text:
        log_warning("meeting.title.empty", user_id=message.chat.id)
        return await manager.answer_and_retry("There is no text in your message")
    log_info("meeting.title.accepted", user_id=message.chat.id, title=message.text[:64])
    await manager.state.update_data({"title": message.text})
    await manager.switch_to(MeetingStates.create, show_mode=ShowMode.DELETE_AND_SEND)


async def open_announce_confirm(query: CallbackQuery, _, manager: DialogManager):
    manager = extend_dialog(manager)
    meeting = await manager.state.get_meeting()
    log_info("meeting.announce.requested", user_id=query.from_user.id, meeting_id=meeting.id)
    try:
        meeting._check_for_announce()
    except Exception as e:
        log_warning(
            "meeting.announce.precondition_failed", user_id=query.from_user.id, meeting_id=meeting.id, reason=str(e)
        )
        return await query.answer(f"{e}", show_alert=True)
    log_info("meeting.announce.confirm_opened", user_id=query.from_user.id, meeting_id=meeting.id)
    await manager.switch_to(state=MeetingStates.announce_confirm)


async def on_announce_confirmed(query: CallbackQuery, _, manager: DialogManager):
    manager = extend_dialog(manager)
    meeting_id = None
    try:
        async with manager.state.sync_meeting() as meeting:
            meeting_id = meeting.id
            log_info("meeting.announce.confirmed", user_id=query.from_user.id, meeting_id=meeting_id)
            await announce_meeting(meeting)
    except Exception as e:
        log_error("meeting.announce.failed", user_id=query.from_user.id, meeting_id=meeting_id, reason=str(e))
        return await query.answer(f"Error: {e}", show_alert=True)
    log_info("meeting.announce.succeeded", user_id=query.from_user.id, meeting_id=meeting_id)
    await query.answer("Meeting announced 🚀", show_alert=True)
    await manager.switch_to(state=MeetingStates.info, show_mode=ShowMode.DELETE_AND_SEND)


async def on_delete_confirmed(query: CallbackQuery, _, manager: DialogManager):
    manager = extend_dialog(manager)
    meeting_id = None
    try:
        meeting = await manager.state.get_meeting()
        meeting_id = meeting.id
        log_info("meeting.cancel.confirmed", user_id=query.from_user.id, meeting_id=meeting_id)
        await cancel_meeting(meeting)
        await manager.state.update_data({"meeting": None})
    except Exception as e:
        log_error("meeting.cancel.failed", user_id=query.from_user.id, meeting_id=meeting_id, reason=str(e))
        return await query.answer(f"{e}", show_alert=True)
    log_info("meeting.cancel.succeeded", user_id=query.from_user.id, meeting_id=meeting_id)
    await query.answer("Meeting cancelled 🚮", show_alert=True)
    await manager.switch_to(state=MeetingStates.list, show_mode=ShowMode.DELETE_AND_SEND)


async def open_finish_confirm(query: CallbackQuery, button: Button, manager: DialogManager):
    manager = extend_dialog(manager)
    meeting = await manager.state.get_meeting()
    log_info("meeting.finish.requested", user_id=query.from_user.id, meeting_id=meeting.id)
    if meeting.status != MeetingStatus.CONDUCTING:
        log_warning(
            "meeting.finish.precondition_failed",
            user_id=query.from_user.id,
            meeting_id=meeting.id,
            current_status=meeting.status,
        )
        return await query.answer("Meeting must be CONDUCTING to become FINISHED", show_alert=True)
    log_info("meeting.finish.confirm_opened", user_id=query.from_user.id, meeting_id=meeting.id)
    await manager.switch_to(state=MeetingStates.finish_confirm)


async def on_finish_confirmed(query: CallbackQuery, button: Button, manager: DialogManager):
    manager = extend_dialog(manager)
    meeting_id = None
    try:
        async with manager.state.sync_meeting() as meeting:
            meeting_id = meeting.id
            log_info("meeting.finish.confirmed", user_id=query.from_user.id, meeting_id=meeting_id)
            await finish_meeting(meeting)
    except Exception as e:
        log_error("meeting.finish.failed", user_id=query.from_user.id, meeting_id=meeting_id, reason=str(e))
        return await query.answer(f"Error: {e}", show_alert=True)
    log_info("meeting.finish.succeeded", user_id=query.from_user.id, meeting_id=meeting_id)
    await manager.switch_to(state=MeetingStates.info, show_mode=ShowMode.DELETE_AND_SEND)


async def on_create_submit(query: CallbackQuery, button: Button, manager: DialogManager):
    manager = extend_dialog(manager)
    assert (discipline_dict := await manager.state.get_value("discipline"))
    assert (title := await manager.state.get_value("title"))
    log_info(
        "meeting.create.requested",
        user_id=query.from_user.id,
        discipline_id=discipline_dict["id"],
        title=title[:64],
    )
    try:
        meeting = await create_meeting(title, discipline_dict["id"], manager.chat.id)
    except Exception as e:
        log_error("meeting.create.failed", user_id=query.from_user.id, reason=str(e))
        return await query.answer(f"Error: {e}", show_alert=True)
    log_info("meeting.create.succeeded", user_id=query.from_user.id, meeting_id=meeting.id)
    await manager.state.set_meeting(meeting)
    await manager.state.update_data({"discipline": None, "title": None})
    await manager.switch_to(state=MeetingStates.info)


async def open_send_for_approval_confirm(query: CallbackQuery, button: Button, manager: DialogManager):
    manager = extend_dialog(manager)
    meeting = await manager.state.get_meeting()
    log_info("meeting.ask_approval.requested", user_id=query.from_user.id, meeting_id=meeting.id)
    try:
        meeting._check_for_approval()
    except Exception as e:
        log_warning(
            "meeting.ask_approval.precondition_failed", user_id=query.from_user.id, meeting_id=meeting.id, reason=str(e)
        )
        return await query.answer(f"{e}", show_alert=True)
    log_info("meeting.ask_approval.confirm_opened", user_id=query.from_user.id, meeting_id=meeting.id)
    await manager.switch_to(state=MeetingStates.send_for_approval_confirm)


async def on_send_for_approval_confirmed(query: CallbackQuery, button: Button, manager: DialogManager):
    manager = extend_dialog(manager)
    meeting_id = None
    try:
        async with manager.state.sync_meeting() as meeting:
            meeting_id = meeting.id
            log_info("meeting.ask_approval.confirmed", user_id=query.from_user.id, meeting_id=meeting_id)
            await send_for_approval(meeting)
    except Exception as e:
        log_error("meeting.ask_approval.failed", user_id=query.from_user.id, meeting_id=meeting_id, reason=str(e))
        return await query.answer(f"Error: {e}", show_alert=True)
    log_info("meeting.ask_approval.succeeded", user_id=query.from_user.id, meeting_id=meeting_id)
    await query.answer("Meeting sent for approval 📩\nWait for notification", show_alert=True)
    await manager.switch_to(state=MeetingStates.info, show_mode=ShowMode.DELETE_AND_SEND)
