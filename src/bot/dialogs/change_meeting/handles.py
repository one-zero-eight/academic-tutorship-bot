from datetime import date, datetime

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button

from src.bot.utils import *
from src.db.repositories import meetings_repo

from .getters import *
from .keyboards import *
from .states import *

# region Utils


# endregion


async def get_new_title(message: Message, _: MessageInput, dialog_manager: DialogManager):
    state = get_state(dialog_manager)
    if not message.text:
        raise ValueError("No message.text")

    new_meeting = await meetings_repo.create(title=message.text)
    await state.update_data({"meeting": meeting_to_dto(new_meeting)})
    await dialog_manager.switch_to(state=ChangeStates.init)


async def open_assign_tutor(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    if not query.message:
        raise ValueError("No query.message")

    to_delete = await query.message.answer(text="Click the button to choose a User 👇", reply_markup=CHOOSE_USER_KB)
    await track_message(to_delete, dialog_manager)


async def get_assigned_tutor(message: Message, _: MessageInput, dialog_manager: DialogManager):
    state = get_state(dialog_manager)

    if not message.users_shared:
        raise ValueError("No message.users_shared")
    if not message.bot:
        raise ValueError("No message.bot")
    await clear_messages(dialog_manager)

    shared_user = message.users_shared.users[0]

    meeting = dto_to_meeting(await state.get_value("meeting"))
    if not meeting:
        raise ValueError("No meeting")

    try:
        tutor = await tutors_repo.get(tg_id=shared_user.user_id)
        meeting.assign_tutor(tutor)
        await meetings_repo.save(meeting)
        await state.update_data({"meeting": meeting_to_dto(meeting)})
        await dialog_manager.switch_to(state=ChangeStates.init, show_mode=ShowMode.DELETE_AND_SEND)

    except LookupError:
        to_delete = await message.answer(
            text=f"The user [{shared_user.user_id}] @{shared_user.username} is not a Tutor", reply_markup=CHOOSE_USER_KB
        )
        await track_message(to_delete, dialog_manager)


async def get_meeting_title(message: Message, _: MessageInput, dialog_manager: DialogManager):
    state = get_state(dialog_manager)
    if not message.text:
        raise ValueError("No message.text")

    meeting = dto_to_meeting(await state.get_value("meeting"))
    if not meeting:
        raise ValueError("No meeting")

    meeting.title = message.text
    await meetings_repo.save(meeting)

    await state.update_data({"meeting": meeting_to_dto(meeting)})
    await message.delete()
    await dialog_manager.switch_to(state=ChangeStates.init, show_mode=ShowMode.DELETE_AND_SEND)


async def get_meeting_description(message: Message, _: MessageInput, dialog_manager: DialogManager):
    state = get_state(dialog_manager)

    if not message.text:
        raise ValueError("message.text is None")

    meeting = dto_to_meeting(await state.get_value("meeting"))
    if not meeting:
        raise ValueError("meeting is None")

    meeting.description = message.text
    await meetings_repo.save(meeting)

    await state.update_data({"meeting": meeting_to_dto(meeting)})
    await message.delete()
    await dialog_manager.switch_to(state=ChangeStates.init, show_mode=ShowMode.DELETE_AND_SEND)


async def on_admin_date_selected(query: CallbackQuery, widget, dialog_manager: DialogManager, selected_date: date):
    state = get_state(dialog_manager)
    meeting = dto_to_meeting(await state.get_value("meeting"))
    if not meeting:
        raise ValueError("meeting is None")

    datetime_obj = datetime.combine(selected_date, datetime.min.time())
    if datetime_obj.date() < datetime.now().date():
        return await query.answer("Date cannot be in the past!", show_alert=True)

    meeting.date = int(datetime_obj.timestamp())
    await meetings_repo.save(meeting)

    await state.update_data({"meeting": meeting_to_dto(meeting)})
    await dialog_manager.switch_to(state=ChangeStates.init)


async def get_meeting_duration(message: Message, _: MessageInput, dialog_manager: DialogManager):
    state = get_state(dialog_manager)

    if not message.text:
        raise ValueError("message.text is None")

    meeting = dto_to_meeting(await state.get_value("meeting"))
    if not meeting:
        raise ValueError("meeting is None")

    # TODO: error handle this
    minutes, seconds = map(int, message.text.split(":"))
    meeting.duration = (minutes * 60 + seconds) * 60
    # till this

    await meetings_repo.save(meeting)
    await state.update_data({"meeting": meeting_to_dto(meeting)})
    await message.delete()
    await dialog_manager.switch_to(state=ChangeStates.init, show_mode=ShowMode.DELETE_AND_SEND)


async def on_tutor_blank(query: CallbackQuery, widget: Any, dialog_manager: DialogManager, item_id: str):
    await query.answer("Just for reference")


async def on_cancel_assign_tutor(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    if not query.bot:
        raise ValueError("No query.bot")
    if not query.message:
        raise ValueError("No query.message")
    await clear_messages(dialog_manager)
