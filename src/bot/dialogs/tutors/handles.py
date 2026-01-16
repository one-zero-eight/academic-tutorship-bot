from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button

from src.bot.utils import *
from src.db.repositories import tutors_repo

from .getters import *
from .states import *


async def on_tutor_selected(query: CallbackQuery, widget: Any, dialog_manager: DialogManager, item_id: str):
    tutor = await tutors_repo.get(id=int(item_id))
    await get_state(dialog_manager).update_data({"tutor": tutor_to_dto(tutor)})
    await dialog_manager.switch_to(TutorsStates.info)


async def on_remove_tutor(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    state = get_state(dialog_manager)

    tutor = dto_to_tutor(await state.get_value("tutor"))
    if not tutor:
        raise ValueError("No tutor")

    await tutors_repo.remove(tutor=tutor)
    await state.update_data({"tutor": None})

    await query.answer(f"@{tutor.username} is no longer a Tutor", show_alert=True)
    await dialog_manager.switch_to(TutorsStates.list)


async def open_add_tutor(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    if not query.message:
        raise ValueError("No query.message")

    to_delete = await query.message.answer(text="Click the button to choose a user 👇", reply_markup=CHOOSE_USER_KB)
    await track_message(to_delete, dialog_manager)


async def get_added_tutor(message: Message, _: MessageInput, dialog_manager: DialogManager):
    if not message.bot:
        raise ValueError("No message.bot")
    if not message.users_shared:
        raise ValueError("No message.users_shared")

    await clear_messages(dialog_manager)

    shared_user = message.users_shared.users[0]

    if shared_user.username is None:
        to_delete = await message.answer(text="Tutor must have a username ⚠️", reply_markup=CHOOSE_USER_KB)
        await track_message(to_delete, dialog_manager)
        return await dialog_manager.switch_to(TutorsStates.add, show_mode=ShowMode.DELETE_AND_SEND)

    if await tutors_repo.exists(tg_id=shared_user.user_id):
        to_delete = await message.answer(text="User is already a Tutor ⚠️", reply_markup=CHOOSE_USER_KB)
        await track_message(to_delete, dialog_manager)
        return await dialog_manager.switch_to(TutorsStates.add, show_mode=ShowMode.DELETE_AND_SEND)

    tutor = await tutors_repo.create(
        tg_id=shared_user.user_id,
        username=shared_user.username,
        first_name=shared_user.first_name,
        last_name=shared_user.last_name,
    )
    await get_state(dialog_manager).update_data({"tutor": tutor_to_dto(tutor)})

    await dialog_manager.switch_to(TutorsStates.info, show_mode=ShowMode.DELETE_AND_SEND)
