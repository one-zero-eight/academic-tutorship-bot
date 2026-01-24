from datetime import date, datetime
from typing import Any

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button

from src.bot.dto import *
from src.bot.scheduling import update_meeting_schedule
from src.bot.utils import *
from src.db.repositories import meetings_repo, tutors_repo

from .getters import *
from .keyboards import *
from .states import *


async def on_switch_clear_messages(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await clear_messages(dialog_manager)


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

    to_delete = await query.message.answer(text="Or click the button to choose a User 👇", reply_markup=CHOOSE_USER_KB)
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

    tutor = meeting.tutor

    if tutor:
        try:
            await message.bot.send_message(
                text=(
                    "You are not longer a tutor for Meeting 🕊️\n"
                    f"Title: {meeting.title}\n"
                    f"Date: {meeting.date_human}\n"
                    "\n"
                    "The meeting is no longer accessible from your meetings list"
                ),
                chat_id=tutor.tg_id,
            )
        except Exception as e:
            print(f"Could not send notification to [{tutor.tg_id}] @{tutor.username}, {e}")

    try:
        tutor = await tutors_repo.get(tg_id=shared_user.user_id)
        meeting.assign_tutor(tutor)
        await message.bot.send_message(
            text=(
                "You are assigned to a Meeting 👨‍🏫\n"
                f"Title: {meeting.title}\n"
                f"Date: {meeting.date_human}\n"
                "\n"
                "You can now see the Meeting in your meetings list"
            ),
            chat_id=tutor.tg_id,
        )
        await meetings_repo.save(meeting)
        await state.update_data({"meeting": meeting_to_dto(meeting)})
        await dialog_manager.switch_to(state=ChangeStates.init, show_mode=ShowMode.DELETE_AND_SEND)

    except LookupError:
        to_delete = await message.answer(
            text=f"The user [{shared_user.user_id}] @{shared_user.username} is not a Tutor", reply_markup=CHOOSE_USER_KB
        )
        await track_message(to_delete, dialog_manager)
        return await dialog_manager.switch_to(ChangeStates.tutor, show_mode=ShowMode.DELETE_AND_SEND)

    except TelegramBadRequest:
        to_delete = await message.answer(
            text=f"The user [{shared_user.user_id}] @{shared_user.username} may have blocked the bot",
            reply_markup=CHOOSE_USER_KB,
        )
        await track_message(to_delete, dialog_manager)
        return await dialog_manager.switch_to(ChangeStates.tutor, show_mode=ShowMode.DELETE_AND_SEND)

    except Exception as e:
        to_delete = await message.answer(text=f"Unknown Error: {e}", reply_markup=CHOOSE_USER_KB)
        await track_message(to_delete, dialog_manager)
        return await dialog_manager.switch_to(ChangeStates.tutor, show_mode=ShowMode.DELETE_AND_SEND)


async def get_meeting_title(message: Message, _: MessageInput, dialog_manager: DialogManager):
    await clear_messages(dialog_manager)
    await message.delete()
    state = get_state(dialog_manager)

    if not message.text:
        to_delete = await message.answer("There is no text in your message")
        await track_message(to_delete, dialog_manager)
        return await dialog_manager.switch_to(ChangeStates.title, show_mode=ShowMode.DELETE_AND_SEND)

    meeting = dto_to_meeting(await state.get_value("meeting"))
    if not meeting:
        raise ValueError("No meeting")

    meeting.title = message.text
    await meetings_repo.save(meeting)

    await state.update_data({"meeting": meeting_to_dto(meeting)})
    await dialog_manager.switch_to(state=ChangeStates.init, show_mode=ShowMode.DELETE_AND_SEND)


async def get_meeting_description(message: Message, _: MessageInput, dialog_manager: DialogManager):
    await clear_messages(dialog_manager)
    await message.delete()

    state = get_state(dialog_manager)

    if not message.text:
        to_delete = await message.answer("There is no text in your message")
        await track_message(to_delete, dialog_manager)
        return await dialog_manager.switch_to(ChangeStates.description, show_mode=ShowMode.DELETE_AND_SEND)

    meeting = dto_to_meeting(await state.get_value("meeting"))
    if not meeting:
        raise ValueError("meeting is None")

    meeting.description = message.text
    await meetings_repo.save(meeting)

    await state.update_data({"meeting": meeting_to_dto(meeting)})
    await dialog_manager.switch_to(state=ChangeStates.init, show_mode=ShowMode.DELETE_AND_SEND)


async def on_date_selected(query: CallbackQuery, widget, dialog_manager: DialogManager, selected_date: date):
    state = get_state(dialog_manager)

    if selected_date < datetime.now().date():
        return await query.answer("Date cannot be in the past!", show_alert=True)

    await state.update_data({"selected_date": selected_date.isoformat()})
    await dialog_manager.switch_to(state=ChangeStates.time)


async def get_meeting_time(message: Message, _: MessageInput, dialog_manager: DialogManager):
    state = get_state(dialog_manager)
    await clear_messages(dialog_manager)
    await message.delete()

    if not message.text:
        to_delete = await message.answer("There is no text in your message")
        await track_message(to_delete, dialog_manager)
        return await dialog_manager.switch_to(ChangeStates.time, show_mode=ShowMode.DELETE_AND_SEND)

    try:
        selected_time = parse_time(message.text)
    except ValueError:
        to_delete = await message.answer("Incorrect format, try like that 00:00")
        await track_message(to_delete, dialog_manager)
        return await dialog_manager.switch_to(ChangeStates.time, show_mode=ShowMode.DELETE_AND_SEND)

    selected_date_str: str | None = await state.get_value("selected_date")
    if not selected_date_str:
        raise ValueError("No date")
    selected_date = date.fromisoformat(selected_date_str)

    datetime_obj = datetime.combine(selected_date, selected_time)
    if datetime_obj < datetime.now():
        to_delete = await message.answer("Date cannot be in the past!")
        await track_message(to_delete, dialog_manager)
        return await dialog_manager.switch_to(ChangeStates.time, show_mode=ShowMode.DELETE_AND_SEND)

    meeting: Meeting | None = dto_to_meeting(await state.get_value("meeting"))
    if not meeting:
        raise ValueError("No meeting")

    meeting.date = int(datetime_obj.timestamp())
    await meetings_repo.save(meeting)
    if meeting.status > MeetingStatus.CREATED:
        await update_meeting_schedule(meeting)
    await state.update_data({"meeting": meeting_to_dto(meeting)})

    if (datetime_obj - datetime.now()).days < 1:
        await message.answer(
            text=("Warning ⚠️\nThe meeting would be conducted in less than 24H\n"), reply_markup=DELETE_WARNING_KB
        )

    await dialog_manager.switch_to(state=ChangeStates.init)


async def get_meeting_duration(message: Message, _: MessageInput, dialog_manager: DialogManager):
    state = get_state(dialog_manager)
    await message.delete()

    if not message.text:
        to_delete = await message.answer("There is no text in your message")
        await track_message(to_delete, dialog_manager)
        return await dialog_manager.switch_to(ChangeStates.duration, show_mode=ShowMode.DELETE_AND_SEND)

    try:
        selected_time = parse_time(message.text)
    except ValueError:
        to_delete = await message.answer("Incorrect format, try like that 00:00")
        await track_message(to_delete, dialog_manager)
        return await dialog_manager.switch_to(ChangeStates.duration, show_mode=ShowMode.DELETE_AND_SEND)

    meeting = dto_to_meeting(await state.get_value("meeting"))
    if not meeting:
        raise ValueError("meeting is None")

    meeting.duration = selected_time.hour * 3600 + selected_time.minute * 60
    await meetings_repo.save(meeting)
    if meeting.status > MeetingStatus.CREATED:
        await update_meeting_schedule(meeting)

    await state.update_data({"meeting": meeting_to_dto(meeting)})
    await dialog_manager.switch_to(state=ChangeStates.init, show_mode=ShowMode.DELETE_AND_SEND)


async def on_tutor_blank(query: CallbackQuery, widget: Any, dialog_manager: DialogManager, item_id: str):
    await query.answer("Just for reference")


async def on_cancel_assign_tutor(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    if not query.bot:
        raise ValueError("No query.bot")
    if not query.message:
        raise ValueError("No query.message")
    await clear_messages(dialog_manager)


async def on_tutor_assign(query: CallbackQuery, widget: Any, dialog_manager: DialogManager, item_id: str):
    state = get_state(dialog_manager)

    if not query.message:
        raise ValueError("No query.message.bot")
    message = query.message

    if not message.bot:
        raise ValueError("No message.bot")
    await clear_messages(dialog_manager)

    meeting = dto_to_meeting(await state.get_value("meeting"))
    if not meeting:
        raise ValueError("No meeting")

    tutor = meeting.tutor

    if tutor:
        try:
            await message.bot.send_message(
                text=(
                    "You are not longer a tutor for Meeting 🕊️\n"
                    f"Title: {meeting.title}\n"
                    f"Date: {meeting.date_human}\n"
                    "\n"
                    "The meeting is no longer accessible from your meetings list"
                ),
                chat_id=tutor.tg_id,
            )
        except Exception as e:
            print(f"Could not send notification to [{tutor.tg_id}] @{tutor.username}, {e}")

    try:
        tutor = await tutors_repo.get(id=int(item_id))
        meeting.assign_tutor(tutor)
        await message.bot.send_message(
            text=(
                "You are assigned to a Meeting 👨‍🏫\n"
                f"Title: {meeting.title}\n"
                f"Date: {meeting.date_human}\n"
                "\n"
                "You can now see the Meeting in your meetings list"
            ),
            chat_id=tutor.tg_id,
        )
        await meetings_repo.save(meeting)
        await state.update_data({"meeting": meeting_to_dto(meeting)})
        await dialog_manager.switch_to(state=ChangeStates.init)

    except LookupError:
        return (await query.answer("The tutor is not found (somehow)", show_alert=True),)

    except TelegramBadRequest:
        return await query.answer("The tutor may have blocked the bot.", show_alert=True)

    except Exception as e:
        return await query.answer(f"Unknown Error: {e}", show_alert=True)


async def get_meeting_room(message: Message, _: MessageInput, dialog_manager: DialogManager):
    state = get_state(dialog_manager)
    await clear_messages(dialog_manager)
    await message.delete()

    if not message.text:
        to_delete = await message.answer("There is no text in your message")
        await track_message(to_delete, dialog_manager)
        return await dialog_manager.switch_to(ChangeStates.room, show_mode=ShowMode.DELETE_AND_SEND)

    if len(message.text) > 64:
        to_delete = await message.answer("Length must not be more than 64 simbols")
        await track_message(to_delete, dialog_manager)
        return await dialog_manager.switch_to(ChangeStates.room, show_mode=ShowMode.DELETE_AND_SEND)

    meeting = dto_to_meeting(await state.get_value("meeting"))
    if not meeting:
        raise ValueError("No meeting")

    meeting.room = message.text
    await meetings_repo.save(meeting)

    await state.update_data({"meeting": meeting_to_dto(meeting)})
    await dialog_manager.switch_to(state=ChangeStates.init, show_mode=ShowMode.DELETE_AND_SEND)
