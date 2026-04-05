from aiogram.types import CallbackQuery, Message, SharedUser
from aiogram_dialog import DialogManager, ShowMode

from src.bot.dialog_extension import extend_dialog
from src.bot.logging_ import log_error, log_info, log_warning
from src.bot.user_errors import *
from src.bot.utils import *
from src.db.repositories import tutor_repo

from .getters import *
from .logic import *
from .states import *


def extract_shared_user(message: Message) -> SharedUser:
    if not message.users_shared:
        raise NoMessageUsersShared()
    return message.users_shared.users[0]


async def on_tutor_selected(query: CallbackQuery, __, manager: DialogManager, item_id: str):
    manager = extend_dialog(manager)
    _ = manager.tr
    log_info("tutor.select.requested", user_id=query.from_user.id, tutor_id=item_id)
    try:
        tutor = await tutor_repo.get(id=int(item_id))
    except LookupError:
        log_warning("tutor.select.not_found", user_id=query.from_user.id, tutor_id=item_id)
        return await query.answer(_("Q_TUTOR_NOT_FOUND"), show_alert=True)
    await manager.state.set_tutor(tutor)
    log_info("tutor.select.succeeded", user_id=query.from_user.id, tutor_id=tutor.id)
    await manager.switch_to(TutorsStates.info)


async def on_remove_tutor(query: CallbackQuery, __, manager: DialogManager):
    manager = extend_dialog(manager)
    _ = manager.tr
    try:
        tutor = await manager.state.get_tutor()
        log_info("tutor.remove.requested", user_id=query.from_user.id, tutor_id=tutor.id)
        await remove_tutor(tutor)
        await manager.state.update_data({"tutor": None})
        log_info("tutor.remove.succeeded", user_id=query.from_user.id, tutor_id=tutor.id)
        await query.answer(_("Q_TUTOR_REMOVED", username=tutor.username), show_alert=True)
        await manager.switch_to(TutorsStates.list)
    except TutorStillAssigned:
        log_warning("tutor.remove.blocked_assigned", user_id=query.from_user.id)
        return await query.answer(_("Q_TUTOR_REMOVE_BLOCKED_ASSIGNED"), show_alert=True)
    except Exception as e:
        log_error("tutor.remove.failed", user_id=query.from_user.id, reason=str(e))
        return await query.answer(_("Q_TUTOR_REMOVE_ERROR", error=str(e)))


async def open_add_tutor(query: CallbackQuery, __, manager: DialogManager):
    manager = extend_dialog(manager)
    _ = manager.tr
    log_info("tutor.add.opened", user_id=query.from_user.id)
    choose_user_kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=_("CHOOSE_FROM_CONTACTS_BTN"), request_users=REQUEST_USERS)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await manager.answer_and_track(text=_("Q_TUTOR_ADD_CHOOSE_USER"), reply_markup=choose_user_kb)


async def get_added_tutor(message: Message, __, manager: DialogManager):
    manager = extend_dialog(manager)
    _ = manager.tr
    await manager.clear_messages()
    choose_user_kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=_("CHOOSE_FROM_CONTACTS_BTN"), request_users=REQUEST_USERS)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    try:
        shared_user = extract_shared_user(message)
        log_info("tutor.add.requested", user_id=message.chat.id, shared_user_id=shared_user.user_id)
        if shared_user.username is None:
            raise NoSharedUserUsername()
        tutor = await add_tutor_from_telegram_id(shared_user.user_id)
        await manager.state.set_tutor(tutor)
        log_info("tutor.add.succeeded", user_id=message.chat.id, tutor_id=tutor.id)
        await manager.switch_to(TutorsStates.info, show_mode=ShowMode.DELETE_AND_SEND)
    except NoMessageUsersShared:
        log_warning("tutor.add.invalid_input", user_id=message.chat.id, reason="no_shared_user")
        return await manager.answer_and_retry(_("Q_TUTOR_ADD_NO_SHARED_USERS"), reply_markup=choose_user_kb)
    except NoSharedUserUsername:
        log_warning("tutor.add.invalid_input", user_id=message.chat.id, reason="shared_user_no_username")
        return await manager.answer_and_retry(text=_("Q_TUTOR_ADD_USERNAME_REQUIRED"), reply_markup=choose_user_kb)
    except UserAlreadyTutor:
        log_warning("tutor.add.invalid_input", user_id=message.chat.id, reason="already_tutor")
        return await manager.answer_and_retry(text=_("Q_TUTOR_ADD_ALREADY_TUTOR"), reply_markup=choose_user_kb)
    except Exception as e:
        log_error("tutor.add.failed", user_id=message.chat.id, reason=str(e))
        return await manager.answer_and_retry(_("Q_TUTOR_ADD_UNKNOWN_ERROR", error=str(e)), reply_markup=choose_user_kb)
