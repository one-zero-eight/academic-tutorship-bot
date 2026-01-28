from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button

from src.bot.extended_dialog_manager import extend
from src.bot.user_errors import *
from src.bot.utils import *
from src.db.repositories import tutors_repo

from .getters import *
from .logic import *
from .states import *


async def on_tutor_selected(query: CallbackQuery, widget: Any, manager: DialogManager, item_id: str):
    manager = extend(manager)
    tutor = await tutors_repo.get(id=int(item_id))
    await manager.state.set_tutor(tutor)
    await manager.switch_to(TutorsStates.info)


async def on_remove_tutor(query: CallbackQuery, button: Button, manager: DialogManager):
    manager = extend(manager)
    try:
        tutor = await manager.state.get_tutor()
        await remove_tutor(tutor, manager)
    except TutorStillAssigned:
        return await query.answer(
            (
                "This tutor is assigned to some meetings in states: CREATED or ANNOUNCED. "
                "Assign another tutor to them first"
            ),
            show_alert=True,
        )
    except Exception as e:
        return await query.answer(f"Error: {e}")
    await query.answer(f"@{tutor.username} is no longer a Tutor", show_alert=True)
    await manager.switch_to(TutorsStates.list)


async def open_add_tutor(query: CallbackQuery, button: Button, manager: DialogManager):
    manager = extend(manager)
    await manager.answer_and_track(text="Click the button to choose a user 👇", reply_markup=CHOOSE_USER_KB)


async def get_added_tutor(message: Message, _: MessageInput, manager: DialogManager):
    manager = extend(manager)
    await manager.clear_messages()
    try:
        await add_tutor_from_shared_user(message, manager)
    except NoMessageUsersShared:
        await manager.answer_and_retry("You've shared no users, use the keyboard below", reply_markup=CHOOSE_USER_KB)
    except NoSharedUserUsername:
        await manager.answer_and_retry(text="Tutor must have a username ⚠️", reply_markup=CHOOSE_USER_KB)
    except UserAlreadyTutor:
        await manager.answer_and_retry(text="User is already a Tutor ⚠️", reply_markup=CHOOSE_USER_KB)
    except Exception as e:
        await manager.answer_and_retry(f"Unkown Error, {e}", reply_markup=CHOOSE_USER_KB)
    await manager.switch_to(TutorsStates.info, show_mode=ShowMode.DELETE_AND_SEND)
