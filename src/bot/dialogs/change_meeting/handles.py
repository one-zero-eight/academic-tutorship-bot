from datetime import date, datetime
from typing import Any

from aiogram.types import CallbackQuery, InaccessibleMessage, Message, SharedUser
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import MessageInput

from src.bot.dialog_extension import extend_dialog
from src.bot.user_errors import *
from src.bot.utils import *

from .getters import *
from .keyboards import *
from .logic import *
from .states import *


async def open_assign_tutor(query: CallbackQuery, _, manager: DialogManager):
    manager = extend_dialog(manager)
    await manager.clear_messages()
    if not query.message:
        raise ValueError("No query.message")
    await manager.answer_and_track(text="Or click the button to choose a User 👇", reply_markup=CHOOSE_USER_KB)


async def get_assigned_tutor(message: Message, _, manager: DialogManager):
    manager = extend_dialog(manager)
    await manager.clear_messages()
    await message.delete()
    try:
        shared_user = _extract_shared_user(message)
        async with manager.state.sync_meeting() as meeting:
            await assign_tutor_to_meeting_by_telegram_id(meeting, shared_user.user_id)
    except NoMessageUsersShared:
        return await manager.answer_and_retry("Please, choose a User from either list", reply_markup=CHOOSE_USER_KB)
    except LookupError:
        return await manager.answer_and_retry(
            text=f"The user [{shared_user.user_id}] @{shared_user.username} is not a Tutor", reply_markup=CHOOSE_USER_KB
        )
    except Exception as e:
        return await manager.answer_and_retry(text=f"Unknown Error: {e}", reply_markup=CHOOSE_USER_KB)
    await manager.switch_to(state=ChangeStates.init, show_mode=ShowMode.DELETE_AND_SEND)


async def get_meeting_title(message: Message, _, manager: DialogManager):
    manager = extend_dialog(manager)
    await manager.clear_messages()
    await message.delete()
    try:
        if not message.text:
            raise NoMessageText()
        async with manager.state.sync_meeting() as meeting:
            await update_meeting_title(meeting, message.text)
    except NoMessageText:
        return await manager.answer_and_retry("There is no text in your message")
    await manager.switch_to(state=ChangeStates.init, show_mode=ShowMode.DELETE_AND_SEND)


async def get_meeting_description(message: Message, _, manager: DialogManager):
    manager = extend_dialog(manager)
    await manager.clear_messages()
    await message.delete()
    try:
        if not message.text:
            raise NoMessageText()
        async with manager.state.sync_meeting() as meeting:
            await update_meeting_description(meeting, message.text)
    except NoMessageText:
        return await manager.answer_and_retry("There is no text in your message")
    await manager.switch_to(state=ChangeStates.init, show_mode=ShowMode.DELETE_AND_SEND)


async def on_date_selected(query: CallbackQuery, _, manager: DialogManager, selected_date: date):
    manager = extend_dialog(manager)
    if selected_date < datetime.now().date():
        return await query.answer("Date cannot be in the past!", show_alert=True)
    await manager.state.update_data({"selected_date": selected_date.isoformat()})
    await manager.switch_to(state=ChangeStates.time)


async def get_meeting_time(message: Message, _, manager: DialogManager):
    manager = extend_dialog(manager)
    await manager.clear_messages()
    await message.delete()
    try:
        selected_time = _extract_time(message)
        selected_date_str = await manager.state.get_value("selected_date")
        if not selected_date_str:
            raise ValueError("No date")
        selected_date = date.fromisoformat(selected_date_str)
        meeting_date = combine_meeting_date_time(selected_date, selected_time)
        async with manager.state.sync_meeting() as meeting:
            await update_meeting_date(meeting, meeting_date)
        await _warn_if_date_is_too_soon(meeting_date, message)
    except NoMessageText:
        return await manager.answer_and_retry("There is no text in your message")
    except DateInPast:
        return await manager.answer_and_retry("Date cannot be in the past!")
    except ValueError:
        return await manager.answer_and_retry("Incorrect format, try like that 00:00")
    await manager.switch_to(state=ChangeStates.init, show_mode=ShowMode.DELETE_AND_SEND)


async def get_meeting_duration(message: Message, _: MessageInput, manager: DialogManager):
    manager = extend_dialog(manager)
    await manager.clear_messages()
    await message.delete()
    try:
        selected_time = _extract_time(message)
        async with manager.state.sync_meeting() as meeting:
            await update_meeting_duration(meeting, selected_time)
    except NoMessageText:
        return await manager.answer_and_retry("There is no text in your message")
    except ValueError:
        return await manager.answer_and_retry("Incorrect format, try like that 00:00")
    await manager.switch_to(state=ChangeStates.init, show_mode=ShowMode.DELETE_AND_SEND)


async def on_tutor_assign(query: CallbackQuery, widget: Any, manager: DialogManager, item_id: str):
    manager = extend_dialog(manager)
    await manager.clear_messages()
    try:
        async with manager.state.sync_meeting() as meeting:
            await assign_tutor_to_meeting_by_id(meeting, int(item_id))
    except LookupError:
        return await query.answer("The tutor is not found (somehow)", show_alert=True)
    except Exception as e:
        return await query.answer(f"Unknown Error: {e}", show_alert=True)
    await manager.switch_to(state=ChangeStates.init, show_mode=ShowMode.DELETE_AND_SEND)


async def get_meeting_room(message: Message, _: MessageInput, manager: DialogManager):
    manager = extend_dialog(manager)
    await manager.clear_messages()
    await message.delete()
    if not message.text:
        return await manager.answer_and_retry("There is no text in your message")
    if len(message.text) > MAX_ROOM_LEN:
        return await manager.answer_and_retry("Length must not be more than 64 simbols")
    async with manager.state.sync_meeting() as meeting:
        await update_meeting_room(meeting, message.text)
    await manager.switch_to(state=ChangeStates.init, show_mode=ShowMode.DELETE_AND_SEND)


# region: helpers


def _extract_shared_user(message: Message | InaccessibleMessage | None) -> SharedUser:
    if not message:
        raise ValueError("No message")
    if isinstance(message, InaccessibleMessage):
        raise ValueError("Message Inaccessible")
    if not message.users_shared:
        raise NoMessageUsersShared()
    return message.users_shared.users[0]


def _extract_time(message: Message):
    if not message.text:
        raise NoMessageText()
    return parse_time(message.text)


async def _warn_if_date_is_too_soon(meeting_date: datetime, message: Message):
    if (meeting_date - datetime.now()).days < 1:
        await message.answer(
            text=("Warning ⚠️\nThe meeting would be conducted in less than 24H\n"), reply_markup=DELETE_WARNING_KB
        )
