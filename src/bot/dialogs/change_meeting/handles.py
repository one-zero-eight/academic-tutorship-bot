from datetime import date, datetime
from typing import Annotated, Any

from aiogram.types import CallbackQuery, InaccessibleMessage, Message, SharedUser
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import MessageInput

from src.bot.dialog_extension import extend_dialog
from src.bot.logging_ import log_error, log_info, log_warning
from src.bot.user_errors import *
from src.bot.utils import *

from .getters import *
from .keyboards import *
from .logic import *
from .states import *


async def open_assign_tutor(query: CallbackQuery, __, manager: DialogManager):
    manager = extend_dialog(manager)
    _ = manager.tr
    await manager.clear_messages()
    log_info("meeting.change.assign_tutor.opened", user_id=query.from_user.id)
    if not query.message:
        log_warning("meeting.change.assign_tutor.invalid", user_id=query.from_user.id, reason="no_query_message")
        raise ValueError("No query.message")
    await manager.answer_and_track(_("ASSIGN_TUTOR_ADDITIONAL_PROMPT"), reply_markup=CHOOSE_USER_KB)


async def get_assigned_tutor(message: Message, __, manager: DialogManager):
    manager = extend_dialog(manager)
    _ = manager.tr
    await manager.clear_messages()
    await message.delete()
    try:
        shared_user = _extract_shared_user(message)
        log_info("meeting.change.assign_tutor.requested", user_id=message.chat.id, shared_user_id=shared_user.user_id)
        async with manager.state.sync_meeting() as meeting:
            await assign_tutor_to_meeting_by_telegram_id(meeting, shared_user.user_id)
    except NoMessageUsersShared:
        log_warning("meeting.change.assign_tutor.invalid", user_id=message.chat.id, reason="no_shared_user")
        return await manager.answer_and_retry(_("Q_CHANGE_PICK_USER_FROM_LIST"), reply_markup=CHOOSE_USER_KB)
    except LookupError:
        log_warning("meeting.change.assign_tutor.invalid", user_id=message.chat.id, reason="not_tutor")
        return await manager.answer_and_retry(
            text=_("Q_CHANGE_USER_IS_NOT_TUTOR", user_id=shared_user.user_id, username=shared_user.username),
            reply_markup=CHOOSE_USER_KB,
        )
    except MeetingIsApproving:
        log_warning("meeting.change.assign_tutor.blocked", user_id=message.chat.id, reason="approving")
        return await manager.answer_and_retry(
            text=_("Q_CHANGE_MEETING_APPROVING_CANNOT_CHANGE_TUTOR"),
            reply_markup=CHOOSE_USER_KB,
        )
    except Exception as e:
        log_error("meeting.change.assign_tutor.failed", user_id=message.chat.id, reason=str(e))
        return await manager.answer_and_retry(
            text=_("Q_CHANGE_UNKNOWN_ERROR", error=str(e)),
            reply_markup=CHOOSE_USER_KB,
        )
    log_info("meeting.change.assign_tutor.succeeded", user_id=message.chat.id)
    await manager.switch_to(state=ChangeStates.init, show_mode=ShowMode.DELETE_AND_SEND)


async def get_meeting_title(message: Message, __, manager: DialogManager):
    manager = extend_dialog(manager)
    _ = manager.tr
    await manager.clear_messages()
    await message.delete()
    try:
        if not message.text:
            raise NoMessageText()
        log_info("meeting.change.title.requested", user_id=message.chat.id)
        async with manager.state.sync_meeting() as meeting:
            await update_meeting_title(meeting, message.text)
    except NoMessageText:
        log_warning("meeting.change.title.invalid", user_id=message.chat.id, reason="no_text")
        return await manager.answer_and_retry(_("Q_MEETING_NO_TEXT_IN_MESSAGE"))
    except MeetingIsApproving:
        log_warning("meeting.change.title.blocked", user_id=message.chat.id, reason="approving")
        return await manager.answer_and_retry(
            text=_("Q_CHANGE_MEETING_APPROVING_CANNOT_CHANGE_TITLE"),
            reply_markup=CHOOSE_USER_KB,
        )
    log_info("meeting.change.title.succeeded", user_id=message.chat.id)
    await manager.switch_to(state=ChangeStates.init, show_mode=ShowMode.DELETE_AND_SEND)


async def get_meeting_description(message: Message, __, manager: DialogManager):
    manager = extend_dialog(manager)
    _ = manager.tr
    await manager.clear_messages()
    await message.delete()
    try:
        if not message.text:
            raise NoMessageText()
        log_info("meeting.change.description.requested", user_id=message.chat.id)
        async with manager.state.sync_meeting() as meeting:
            await update_meeting_description(meeting, message.text)
    except NoMessageText:
        log_warning("meeting.change.description.invalid", user_id=message.chat.id, reason="no_text")
        return await manager.answer_and_retry(_("Q_MEETING_NO_TEXT_IN_MESSAGE"))
    except MeetingIsApproving:
        log_warning("meeting.change.description.blocked", user_id=message.chat.id, reason="approving")
        return await manager.answer_and_retry(
            text=_("Q_CHANGE_MEETING_APPROVING_CANNOT_CHANGE_DESCRIPTION"),
            reply_markup=CHOOSE_USER_KB,
        )
    log_info("meeting.change.description.succeeded", user_id=message.chat.id)
    await manager.switch_to(state=ChangeStates.init, show_mode=ShowMode.DELETE_AND_SEND)


async def on_date_selected(query: CallbackQuery, __, manager: DialogManager, selected_date: date):
    manager = extend_dialog(manager)
    _ = manager.tr
    log_info("meeting.change.date.selected", user_id=query.from_user.id, selected_date=selected_date.isoformat())
    if selected_date < datetime.now().date():
        log_warning("meeting.change.date.invalid", user_id=query.from_user.id, reason="in_past")
        return await query.answer(_("Q_CHANGE_DATE_CANNOT_BE_IN_PAST"), show_alert=True)
    await manager.state.update_data({"selected_date": selected_date.isoformat()})
    await manager.switch_to(state=ChangeStates.time)


async def get_meeting_time(message: Message, __, manager: DialogManager):
    manager = extend_dialog(manager)
    _ = manager.tr
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
            log_info("meeting.change.time.requested", user_id=message.chat.id, selected_time=str(selected_time))
            await update_meeting_date(meeting, meeting_date)
        await _warn_if_date_is_too_soon(meeting_date, message, _)
    except NoMessageText:
        log_warning("meeting.change.time.invalid", user_id=message.chat.id, reason="no_text")
        return await manager.answer_and_retry(_("Q_MEETING_NO_TEXT_IN_MESSAGE"))
    except DateInPast:
        log_warning("meeting.change.time.invalid", user_id=message.chat.id, reason="date_in_past")
        return await manager.answer_and_retry(_("Q_CHANGE_DATE_CANNOT_BE_IN_PAST"))
    except ValueError:
        log_warning("meeting.change.time.invalid", user_id=message.chat.id, reason="bad_format")
        return await manager.answer_and_retry(_("Q_CHANGE_INVALID_TIME_FORMAT"))
    log_info("meeting.change.time.succeeded", user_id=message.chat.id, new_datetime=meeting_date.isoformat())
    await manager.switch_to(state=ChangeStates.init, show_mode=ShowMode.DELETE_AND_SEND)


async def get_meeting_duration(message: Message, __: MessageInput, manager: DialogManager):
    manager = extend_dialog(manager)
    _ = manager.tr
    await manager.clear_messages()
    await message.delete()
    try:
        selected_time = _extract_time(message)
        log_info("meeting.change.duration.requested", user_id=message.chat.id, selected_time=str(selected_time))
        async with manager.state.sync_meeting() as meeting:
            await update_meeting_duration(meeting, selected_time)
    except NoMessageText:
        log_warning("meeting.change.duration.invalid", user_id=message.chat.id, reason="no_text")
        return await manager.answer_and_retry(_("Q_MEETING_NO_TEXT_IN_MESSAGE"))
    except ValueError:
        log_warning("meeting.change.duration.invalid", user_id=message.chat.id, reason="bad_format")
        return await manager.answer_and_retry(_("Q_CHANGE_INVALID_TIME_FORMAT"))
    except MeetingIsApproving:
        log_warning("meeting.change.duration.blocked", user_id=message.chat.id, reason="approving")
        return await manager.answer_and_retry(
            text=_("Q_CHANGE_MEETING_APPROVING_CANNOT_CHANGE_DURATION"),
            reply_markup=CHOOSE_USER_KB,
        )
    log_info("meeting.change.duration.succeeded", user_id=message.chat.id)
    await manager.switch_to(state=ChangeStates.init, show_mode=ShowMode.DELETE_AND_SEND)


async def on_tutor_assign(query: CallbackQuery, __: Any, manager: DialogManager, item_id: str):
    manager = extend_dialog(manager)
    _ = manager.tr
    await manager.clear_messages()
    try:
        log_info("meeting.change.tutor.assign.requested", user_id=query.from_user.id, tutor_id=item_id)
        async with manager.state.sync_meeting() as meeting:
            await assign_tutor_to_meeting_by_id(meeting, int(item_id))
    except LookupError:
        log_warning("meeting.change.tutor.assign.invalid", user_id=query.from_user.id, reason="not_found")
        return await query.answer(_("Q_CHANGE_TUTOR_NOT_FOUND"), show_alert=True)
    except MeetingIsApproving:
        log_warning("meeting.change.tutor.assign.blocked", user_id=query.from_user.id, reason="approving")
        return await query.answer(text=_("Q_CHANGE_MEETING_APPROVING_CANNOT_CHANGE_TUTOR"), show_alert=True)
    except Exception as e:
        log_error("meeting.change.tutor.assign.failed", user_id=query.from_user.id, reason=str(e))
        return await query.answer(_("Q_CHANGE_UNKNOWN_ERROR", error=str(e)), show_alert=True)
    log_info("meeting.change.tutor.assign.succeeded", user_id=query.from_user.id, tutor_id=item_id)
    await manager.switch_to(state=ChangeStates.init, show_mode=ShowMode.DELETE_AND_SEND)


async def get_meeting_room(message: Message, __: MessageInput, manager: DialogManager):
    manager = extend_dialog(manager)
    _ = manager.tr
    await manager.clear_messages()
    await message.delete()
    try:
        if not message.text:
            raise NoMessageText()
        if len(message.text) > MAX_ROOM_LEN:
            raise ValueError("Length must not be more than 64 simbols")
        log_info("meeting.change.room.requested", user_id=message.chat.id, room=message.text[:64])
        async with manager.state.sync_meeting() as meeting:
            await update_meeting_room(meeting, message.text)
    except NoMessageText:
        log_warning("meeting.change.room.invalid", user_id=message.chat.id, reason="no_text")
        return await manager.answer_and_retry(_("Q_MEETING_NO_TEXT_IN_MESSAGE"))
    except ValueError as e:
        log_warning("meeting.change.room.invalid", user_id=message.chat.id, reason=str(e))
        return await manager.answer_and_retry(_("Q_CHANGE_ROOM_INVALID_FORMAT", error=str(e)))
    except MeetingIsApproving:
        log_warning("meeting.change.room.blocked", user_id=message.chat.id, reason="approving")
        return await manager.answer_and_retry(
            text=_("Q_CHANGE_MEETING_APPROVING_CANNOT_CHANGE_ROOM"),
            reply_markup=CHOOSE_USER_KB,
        )
    log_info("meeting.change.room.succeeded", user_id=message.chat.id)
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


async def _warn_if_date_is_too_soon(
    meeting_date: datetime, message: Message, tr: Annotated[Any, "Translation function"]
):
    delete_warning_kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=tr("DELETE_WARNING_BTN"), callback_data="delete_warning")]]
    )
    if (meeting_date - datetime.now()).days < 1:
        await message.answer(
            text=tr("Q_CHANGE_MEETING_TOO_SOON_WARNING"),
            reply_markup=delete_warning_kb,
        )
