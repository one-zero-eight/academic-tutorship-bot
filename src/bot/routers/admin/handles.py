from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode, StartMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button

from src.bot.utils import *

from .getters import *
from .keyboards import *
from .states import *


async def open_menu(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(AdminStates.start, mode=StartMode.RESET_STACK)


async def open_admin_menu(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(AdminStates.start, mode=StartMode.RESET_STACK)


async def on_tutor_selected(query: CallbackQuery, widget: Any, dialog_manager: DialogManager, item_id: str):
    tutor = await tutors_repo.get(id=int(item_id))
    dialog_manager.dialog_data.update({"tutor": tutor_to_dto(tutor)})
    await dialog_manager.switch_to(AdminStates.tutor_info)


async def on_tutor_blank(query: CallbackQuery, widget: Any, dialog_manager: DialogManager, item_id: str):
    await query.answer("Just for reference")


async def on_remove_tutor(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    tutor: Tutor | None = dto_to_tutor(dialog_manager.dialog_data.pop("tutor", None))
    if not tutor:
        raise ValueError("No tutor")  # noqa E701

    await tutors_repo.remove(tutor=tutor)
    await query.answer(f"@{tutor.username} is no longer a Tutor", show_alert=True)
    await dialog_manager.switch_to(AdminStates.tutors_list)


async def open_add_tutor(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    if not query.message:
        raise ValueError("No query.message")  # noqa E701

    to_delete = await query.message.answer(text="Click the button to choose a user 👇", reply_markup=CHOOSE_USER_KB)
    dialog_manager.dialog_data.update({"to_delete_id": to_delete.message_id})

    await dialog_manager.switch_to(AdminStates.add_tutor)


async def get_added_tutor(message: Message, _: MessageInput, dialog_manager: DialogManager):
    if not message.bot:
        raise ValueError("No message.bot")  # noqa E701
    if not message.users_shared:
        raise ValueError("No message.users_shared")  # noqa E701

    await clear_messages(dialog_manager)

    shared_user = message.users_shared.users[0]

    if shared_user.username is None:
        to_delete = await message.answer(text="Tutor must have a username ⚠️", reply_markup=CHOOSE_USER_KB)
        dialog_manager.dialog_data.update({"to_delete_id": to_delete.message_id})
        return await dialog_manager.switch_to(AdminStates.add_tutor, show_mode=ShowMode.DELETE_AND_SEND)

    if await tutors_repo.exists(tg_id=shared_user.user_id):
        to_delete = await message.answer(text="User is already a Tutor ⚠️", reply_markup=CHOOSE_USER_KB)
        dialog_manager.dialog_data.update({"to_delete_id": to_delete.message_id})
        return await dialog_manager.switch_to(AdminStates.add_tutor, show_mode=ShowMode.DELETE_AND_SEND)

    tutor = await tutors_repo.create(
        tg_id=shared_user.user_id,
        username=shared_user.username,
        first_name=shared_user.first_name,
        last_name=shared_user.last_name,
    )
    dialog_manager.dialog_data.update({"tutor": tutor_to_dto(tutor)})

    await dialog_manager.switch_to(AdminStates.tutor_info, show_mode=ShowMode.DELETE_AND_SEND)


async def open_tutors_list_with_clear(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    if not query.bot:
        raise ValueError("No query.bot")  # noqa: E701
    if not query.message:
        raise ValueError("No query.message")  # noqa: E701
    if not button.widget_id:
        raise ValueError("No button.widget_id")  # noqa: E701

    await clear_messages(dialog_manager)
    await dialog_manager.switch_to(AdminStates.tutors_list)
