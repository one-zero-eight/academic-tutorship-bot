from typing import Literal

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Button

from src.bot.dialog_extension import extend_dialog
from src.bot.user_errors import *
from src.bot.utils import *
from src.db.repositories import meeting_repo
from src.domain.models import MeetingStatus

from .logic import *
from .states import *


async def on_meeting_selected(query: CallbackQuery, meeting, manager: DialogManager, item_id: str):
    manager = extend_dialog(manager)
    meeting = await meeting_repo.get(int(item_id))
    await manager.state.set_meeting(meeting)
    await manager.switch_to(MeetingStates.info)


def open_meetings_list_of_type(type: Literal["created", "announced", "closed"]):
    """Higher order function, returns Awaitable that opens specified meetings list"""

    async def open_meetings_list(query: CallbackQuery, _, manager: DialogManager):
        manager = extend_dialog(manager)
        await manager.state.update_data({"meetings_type": type})
        await manager.switch_to(MeetingStates.list)

    return open_meetings_list


async def get_new_title(message: Message, _, manager: DialogManager):
    manager = extend_dialog(manager)
    await manager.clear_messages()
    await message.delete()
    if not message.text:
        return await manager.answer_and_retry("There is no text in your message")
    await manager.state.update_data({"title": message.text})
    await manager.switch_to(MeetingStates.create, show_mode=ShowMode.DELETE_AND_SEND)


async def open_announce_confirm(query: CallbackQuery, _, manager: DialogManager):
    manager = extend_dialog(manager)
    meeting = await manager.state.get_meeting()
    try:
        meeting._check_for_announce()
    except Exception as e:
        return await query.answer(f"{e}", show_alert=True)
    await manager.switch_to(state=MeetingStates.announce_confirm)


async def on_announce_confirmed(query: CallbackQuery, _, manager: DialogManager):
    manager = extend_dialog(manager)
    try:
        async with manager.state.sync_meeting() as meeting:
            await announce_meeting(meeting)
    except Exception as e:
        return await query.answer(f"Error: {e}", show_alert=True)
    await query.answer("Meeting announced 🚀", show_alert=True)
    await manager.switch_to(state=MeetingStates.info, show_mode=ShowMode.DELETE_AND_SEND)


async def on_delete_confirmed(query: CallbackQuery, _, manager: DialogManager):
    manager = extend_dialog(manager)
    try:
        meeting = await manager.state.get_meeting()
        await delete_meeting(meeting)
        await manager.state.update_data({"meeting": None})
    except Exception as e:
        return await query.answer(f"{e}", show_alert=True)
    await query.answer("Meeting deleted", show_alert=True)
    await manager.switch_to(state=MeetingStates.list, show_mode=ShowMode.DELETE_AND_SEND)


async def open_finish_confirm(query: CallbackQuery, button: Button, manager: DialogManager):
    manager = extend_dialog(manager)
    meeting = await manager.state.get_meeting()
    if meeting.status != MeetingStatus.CONDUCTING:
        return await query.answer("Meeting must be CONDUCTING to become FINISHED", show_alert=True)
    await manager.switch_to(state=MeetingStates.finish_confirm)


async def on_finish_confirmed(query: CallbackQuery, button: Button, manager: DialogManager):
    manager = extend_dialog(manager)
    try:
        async with manager.state.sync_meeting() as meeting:
            await finish_meeting(meeting)
    except Exception as e:
        return await query.answer(f"Error: {e}", show_alert=True)
    await manager.switch_to(state=MeetingStates.info, show_mode=ShowMode.DELETE_AND_SEND)


async def on_create_submit(query: CallbackQuery, button: Button, manager: DialogManager):
    manager = extend_dialog(manager)
    assert (discipline_dict := await manager.state.get_value("discipline"))
    assert (title := await manager.state.get_value("title"))
    meeting = await create_meeting(title, discipline_dict["id"], manager.chat.id)
    await manager.state.set_meeting(meeting)
    await manager.state.update_data({"discipline": None, "title": None})
    await manager.switch_to(state=MeetingStates.info)


async def open_send_for_approval_confirm(query: CallbackQuery, button: Button, manager: DialogManager):
    manager = extend_dialog(manager)
    meeting = await manager.state.get_meeting()
    try:
        meeting._check_for_approval()
    except Exception as e:
        return await query.answer(f"{e}", show_alert=True)
    await manager.switch_to(state=MeetingStates.send_for_approval_confirm)


async def on_send_for_approval_confirmed(query: CallbackQuery, button: Button, manager: DialogManager):
    manager = extend_dialog(manager)
    try:
        async with manager.state.sync_meeting() as meeting:
            await send_for_approval(meeting)
    except Exception as e:
        return await query.answer(f"Error: {e}", show_alert=True)
    await query.answer("Meeting sent for approval 📩\nWait for notification", show_alert=True)
    await manager.switch_to(state=MeetingStates.info, show_mode=ShowMode.DELETE_AND_SEND)
