from datetime import date, datetime
from typing import Any

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button

from src.bot.dialog_extension import extend_dialog
from src.bot.dto import *
from src.bot.user_errors import *
from src.bot.utils import *

from .getters import *
from .keyboards import *
from .logic import *
from .states import *


async def open_assign_tutor(query: CallbackQuery, button: Button, manager: DialogManager):
    manager = extend_dialog(manager)
    await manager.clear_messages()
    if not query.message:
        raise ValueError("No query.message")
    await manager.answer_and_track(text="Or click the button to choose a User 👇", reply_markup=CHOOSE_USER_KB)


async def get_assigned_tutor(message: Message, _: MessageInput, manager: DialogManager):
    manager = extend_dialog(manager)
    await manager.clear_messages()
    await message.delete()
    try:
        shared_user = extract_shared_user(message)
        await update_meeting_tutor_shared_user(shared_user, manager)
    except NoMessageUsersShared:
        return await manager.answer_and_retry("Please, choose a User from either list", reply_markup=CHOOSE_USER_KB)
    except LookupError:
        return await manager.answer_and_retry(
            text=f"The user [{shared_user.user_id}] @{shared_user.username} is not a Tutor", reply_markup=CHOOSE_USER_KB
        )
    except Exception as e:
        return await manager.answer_and_retry(text=f"Unknown Error: {e}", reply_markup=CHOOSE_USER_KB)
    await manager.switch_to(state=ChangeStates.init, show_mode=ShowMode.DELETE_AND_SEND)


async def get_meeting_title(message: Message, _: MessageInput, manager: DialogManager):
    manager = extend_dialog(manager)
    await manager.clear_messages()
    await message.delete()
    try:
        await update_meeting_title(message, manager)
    except NoMessageText:
        return await manager.answer_and_retry("There is no text in your message")
    await manager.switch_to(state=ChangeStates.init, show_mode=ShowMode.DELETE_AND_SEND)


async def get_meeting_description(message: Message, _: MessageInput, manager: DialogManager):
    manager = extend_dialog(manager)
    await manager.clear_messages()
    await message.delete()
    try:
        await update_meeting_description(message, manager)
    except NoMessageText:
        return await manager.answer_and_retry("There is no text in your message")
    await manager.switch_to(state=ChangeStates.init, show_mode=ShowMode.DELETE_AND_SEND)


async def on_date_selected(query: CallbackQuery, widget, manager: DialogManager, selected_date: date):
    manager = extend_dialog(manager)
    if selected_date < datetime.now().date():
        return await query.answer("Date cannot be in the past!", show_alert=True)
    await manager.state.update_data({"selected_date": selected_date.isoformat()})
    await manager.switch_to(state=ChangeStates.time)


async def get_meeting_time(message: Message, _: MessageInput, manager: DialogManager):
    manager = extend_dialog(manager)
    await manager.clear_messages()
    await message.delete()
    try:
        selected_time = extract_time(message)
        meeting_date = await combine_meeting_date_time(selected_time, manager)
        await update_meeting_date(meeting_date, manager)
        await warn_if_date_is_too_soon(meeting_date, message)
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
        selected_time = extract_time(message)
        await update_meeting_duration(selected_time, manager)
    except NoMessageText:
        return await manager.answer_and_retry("There is no text in your message")
    except ValueError:
        return await manager.answer_and_retry("Incorrect format, try like that 00:00")
    await manager.switch_to(state=ChangeStates.init, show_mode=ShowMode.DELETE_AND_SEND)


async def on_tutor_assign(query: CallbackQuery, widget: Any, manager: DialogManager, item_id: str):
    manager = extend_dialog(manager)
    await manager.clear_messages()
    try:
        await update_meeting_tutor_item_id(item_id, manager)
    except LookupError:
        return await query.answer("The tutor is not found (somehow)", show_alert=True)
    except Exception as e:
        return await query.answer(f"Unknown Error: {e}", show_alert=True)
    await manager.switch_to(state=ChangeStates.init, show_mode=ShowMode.DELETE_AND_SEND)


async def get_meeting_room(message: Message, _: MessageInput, manager: DialogManager):
    manager = extend_dialog(manager)
    await manager.clear_messages()
    await message.delete()
    try:
        await update_meeting_room(message, manager)
    except NoMessageText:
        return await manager.answer_and_retry("There is no text in your message")
    except RoomTooLong:
        return await manager.answer_and_retry("Length must not be more than 64 simbols")
    await manager.switch_to(state=ChangeStates.init, show_mode=ShowMode.DELETE_AND_SEND)
