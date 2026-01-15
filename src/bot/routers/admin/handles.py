from datetime import date, datetime
from typing import Literal

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode, StartMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button

from .getters import *
from .keyboards import *
from .states import *
from .utils import *


async def open_menu(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(AdminStates.start, mode=StartMode.RESET_STACK)


async def open_meetings_type_choice(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminStates.meetings_type)


def open_meetings_list_of_type(type: Literal["created", "announced", "closed"]):
    """Higher order function, returns Awaitable that opens specified meetings list"""

    async def open_meetings_list(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
        dialog_manager.dialog_data.update({"meetings_type": type})
        await dialog_manager.switch_to(AdminStates.meetings_list)

    return open_meetings_list


async def open_meeting_create(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminStates.create_meeting)


async def open_admin_menu(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(AdminStates.start, mode=StartMode.RESET_STACK)


async def open_meeting_info(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    if not query.bot:
        raise ValueError("No query.bot")  # noqa E701
    if not query.message:
        raise ValueError("No query.message")  # noqa E701
    if not button.widget_id:
        raise ValueError("No button.widget_id")  # noqa E701

    await clear_messages(query.bot, dialog_manager, query.message.chat)

    if button.widget_id.startswith("a_meeting"):
        meeting_id = int(button.widget_id.replace("a_meeting_", ""))
        meeting = await meetings_repo.get(id=meeting_id)
        dialog_manager.dialog_data.update({"meeting": meeting_to_dto(meeting)})

    await dialog_manager.switch_to(AdminStates.meeting_info)


async def get_new_title(message: Message, _: MessageInput, dialog_manager: DialogManager):
    if not message.text:
        raise ValueError("No message.text")  # noqa E701

    new_meeting = await meetings_repo.create(title=message.text)
    dialog_manager.dialog_data.update({"meeting": meeting_to_dto(new_meeting)})
    await dialog_manager.switch_to(AdminStates.meeting_info)


async def on_meeting_selected(query: CallbackQuery, widget: Any, dialog_manager: DialogManager, item_id: str):
    meeting = await meetings_repo.get(id=int(item_id))
    dialog_manager.dialog_data.update({"meeting": meeting_to_dto(meeting)})
    await dialog_manager.switch_to(AdminStates.meeting_info)


async def open_assign_tutor(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    if not query.message:
        raise ValueError("No query.message")  # noqa E701
    to_delete = await query.message.answer(text="Click the button to choose a User 👇", reply_markup=CHOOSE_USER_KB)
    dialog_manager.dialog_data.update({"to_delete_id": to_delete.message_id})
    await dialog_manager.switch_to(AdminStates.assign_tutor)


async def open_set_title(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminStates.set_title)


async def open_set_description(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminStates.set_description)


async def open_set_date(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminStates.set_date)


async def open_set_duration(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminStates.set_duration)


async def get_assigned_tutor(message: Message, _: MessageInput, dialog_manager: DialogManager):
    if not message.users_shared:
        raise ValueError("No message.users_shared")  # noqa E701
    if not message.bot:
        raise ValueError("No message.bot")  # noqa E701
    await clear_messages(message.bot, dialog_manager, message.chat)

    shared_user = message.users_shared.users[0]

    meeting: Meeting | None = dto_to_meeting(dialog_manager.dialog_data.get("meeting"))
    if not meeting:
        raise ValueError("No meeting")  # noqa E701

    tutor = await tutors_repo.get(tg_id=shared_user.user_id)
    meeting.assign_tutor(tutor)
    await meetings_repo.save(meeting)

    dialog_manager.dialog_data.update({"meeting": meeting_to_dto(meeting)})
    await dialog_manager.switch_to(AdminStates.meeting_change, show_mode=ShowMode.DELETE_AND_SEND)


async def get_meeting_title(message: Message, _: MessageInput, dialog_manager: DialogManager):
    if not message.text:
        raise ValueError("No message.text")  # noqa E701

    meeting: Meeting | None = dto_to_meeting(dialog_manager.dialog_data.get("meeting"))
    if not meeting:
        raise ValueError("No meeting")  # noqa E701

    meeting.title = message.text
    await meetings_repo.save(meeting)

    dialog_manager.dialog_data.update({"meeting": meeting_to_dto(meeting)})
    await message.delete()
    await dialog_manager.switch_to(AdminStates.meeting_change, show_mode=ShowMode.DELETE_AND_SEND)


async def get_meeting_description(message: Message, _: MessageInput, dialog_manager: DialogManager):
    if not message.text:
        raise ValueError("message.text is None")  # noqa E701

    meeting: Meeting | None = dto_to_meeting(dialog_manager.dialog_data.get("meeting"))
    if not meeting:
        raise ValueError("meeting is None")  # noqa E701

    meeting.description = message.text
    await meetings_repo.save(meeting)

    dialog_manager.dialog_data.update({"meeting": meeting_to_dto(meeting)})
    await message.delete()
    await dialog_manager.switch_to(AdminStates.meeting_change, show_mode=ShowMode.DELETE_AND_SEND)


async def on_admin_date_selected(query: CallbackQuery, widget, dialog_manager: DialogManager, selected_date: date):
    meeting: Meeting | None = dto_to_meeting(dialog_manager.dialog_data.get("meeting"))
    if not meeting:
        raise ValueError("meeting is None")  # noqa E701

    datetime_obj = datetime.combine(selected_date, datetime.min.time())
    if datetime_obj.date() < datetime.now().date():
        return await query.answer("Date cannot be in the past!", show_alert=True)

    meeting.date = int(datetime_obj.timestamp())
    await meetings_repo.save(meeting)

    dialog_manager.dialog_data.update({"meeting": meeting_to_dto(meeting)})
    await dialog_manager.switch_to(AdminStates.meeting_change)


async def get_meeting_duration(message: Message, _: MessageInput, dialog_manager: DialogManager):
    if not message.text:
        raise ValueError("message.text is None")  # noqa E701

    meeting: Meeting | None = dto_to_meeting(dialog_manager.dialog_data.get("meeting"))
    if not meeting:
        raise ValueError("meeting is None")  # noqa E701

    # TODO: error handle this
    minutes, seconds = map(int, message.text.split(":"))
    meeting.duration = (minutes * 60 + seconds) * 60
    # till this

    await meetings_repo.save(meeting)
    dialog_manager.dialog_data.update({"meeting": meeting_to_dto(meeting)})
    await message.delete()
    await dialog_manager.switch_to(AdminStates.meeting_change, show_mode=ShowMode.DELETE_AND_SEND)


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

    await clear_messages(message.bot, dialog_manager, message.chat)

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

    await clear_messages(query.bot, dialog_manager, query.message.chat)
    await dialog_manager.switch_to(AdminStates.tutors_list)
