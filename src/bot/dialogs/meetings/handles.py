from datetime import datetime
from typing import Literal

from aiogram import Bot
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Button

from src.bot.dto import *
from src.bot.scheduling import update_meeting_schedule, wipe_meeting_schedule
from src.bot.utils import *
from src.config import settings
from src.db.repositories import meetings_repo

from .states import *


async def on_meeting_selected(query: CallbackQuery, meeting, dialog_manager: DialogManager, item_id: str):
    meeting = await meetings_repo.get(id=int(item_id))
    await get_state(dialog_manager).update_data({"meeting": meeting_to_dto(meeting)})
    await dialog_manager.switch_to(MeetingStates.info)


def open_meetings_list_of_type(type: Literal["created", "announced", "closed"]):
    """Higher order function, returns Awaitable that opens specified meetings list"""

    async def open_meetings_list(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
        await get_state(dialog_manager).update_data({"meetings_type": type})
        await dialog_manager.switch_to(MeetingStates.list)

    return open_meetings_list


async def open_meeting_create(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(MeetingStates.create)


async def get_new_title(message: Message, message_input, dialog_manager: DialogManager):
    if not message.text:
        raise ValueError("No message.text")  # noqa E701

    new_meeting = await meetings_repo.create(title=message.text)
    await get_state(dialog_manager).update_data({"meeting": meeting_to_dto(new_meeting)})
    await dialog_manager.switch_to(MeetingStates.info, show_mode=ShowMode.DELETE_AND_SEND)
    await message.delete()


async def open_announce_confirm(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    state = get_state(dialog_manager)
    meeting = dto_to_meeting(await state.get_value("meeting"))
    if not meeting:
        raise ValueError("No meeting")

    try:
        meeting._check_for_announce()
    except Exception as e:
        return await query.answer(f"{e}", show_alert=True)

    await dialog_manager.switch_to(state=MeetingStates.announce_confirm)


async def on_announce_confirmed(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    state = get_state(dialog_manager)
    bot: Bot = dialog_manager.middleware_data["bot"]

    meeting = dto_to_meeting(await state.get_value("meeting"))
    if not meeting:
        raise ValueError("No meeting")

    try:
        meeting.announce()
        await update_meeting_schedule(meeting)

    except Exception as e:
        return await query.answer(f"{e}", show_alert=True)

    await meetings_repo.save(meeting)
    await state.update_data({"meeting": meeting_to_dto(meeting)})

    tutor = meeting.tutor
    if not tutor:
        raise ValueError("No tutor")

    for chat_id in list(set(settings.admins + [tutor.tg_id])):
        try:
            await bot.send_message(
                text=(
                    "A meeting was announced 📣\n"
                    f'Title: "{meeting.title}"\n'
                    f"Date: {meeting.date_human}\n"
                    f"Tutor: @{tutor.username}"
                ),
                chat_id=chat_id,
            )
        except Exception as e:
            print(f"Error sending notification to [{chat_id}], {e}")

    await query.answer("Okay, announced", show_alert=True)

    # TODO LATER:
    #       - for the students who want notifications

    await dialog_manager.switch_to(state=MeetingStates.info, show_mode=ShowMode.DELETE_AND_SEND)


async def open_delete_confirm(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    state = get_state(dialog_manager)
    meeting = dto_to_meeting(await state.get_value("meeting"))
    if not meeting:
        raise ValueError("No meeting")

    await dialog_manager.switch_to(state=MeetingStates.delete_confirm)


async def on_delete_confirmed(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    state = get_state(dialog_manager)
    bot: Bot = dialog_manager.middleware_data["bot"]

    meeting = dto_to_meeting(await state.get_value("meeting"))
    if not meeting:
        raise ValueError("No meeting")

    try:
        await meetings_repo.remove(meeting=meeting)
        await wipe_meeting_schedule(meeting)
    except Exception as e:
        return await query.answer(f"{e}", show_alert=True)

    await state.update_data({"meeting": None})

    listeners = settings.admins.copy()
    if tutor := meeting.tutor:
        listeners = list(set(listeners + [tutor.tg_id]))

    for chat_id in listeners:
        try:
            await bot.send_message(
                text=("A meeting was deleted 🗑️\n" f'Title: "{meeting.title}"\n' f"Date: {meeting.date_human}\n"),
                chat_id=chat_id,
            )
        except Exception as e:
            print(f"Error sending notification to [{chat_id}], {e}")

    await query.answer("Meeting deleted", show_alert=True)

    # TODO LATER:
    #       - for the students who want notifications

    await dialog_manager.switch_to(state=MeetingStates.list, show_mode=ShowMode.DELETE_AND_SEND)


async def open_finish_confirm(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    state = get_state(dialog_manager)
    meeting = dto_to_meeting(await state.get_value("meeting"))
    if not meeting:
        raise ValueError("No meeting")

    if meeting.status != MeetingStatus.CONDUCTING:
        return await query.answer("Meeting must be CONDUCTING to become FINISHED", show_alert=True)

    await dialog_manager.switch_to(state=MeetingStates.finish_confirm)


async def on_finish_confirmed(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    state = get_state(dialog_manager)

    meeting = dto_to_meeting(await state.get_value("meeting"))
    if not meeting:
        raise ValueError("No meeting")

    try:
        meeting.finish()
        _adjust_duration(meeting)
        await state.update_data({"meeting": meeting_to_dto(meeting)})
        await meetings_repo.save(meeting)
        await wipe_meeting_schedule(meeting)
        print(f"Meeting [{meeting.id}] finished")
        await send_to_admins(
            meeting,
            text=(
                f'Meeting "{meeting.title}" finished ☑️ \n'
                f'Date: {meeting.date_human}\n'
                f'Duration: {meeting.duration_human}\n'
                f'Tutor: @{meeting.tutor.username if meeting.tutor else "---"}\n'
            ),
        )
        await send_to_tutor(
            meeting,
            text=(
                f'Meeting "{meeting.title}" finished ☑️ \n'
                f'Date: {meeting.date_human}\n'
                f'Duration: {meeting.duration_human}\n'
                f'Tutor: @{meeting.tutor.username if meeting.tutor else "---"}\n'
                '\nSend an Attendance File to close the Meeting!'
            ),
            reply_markup=create_attendance_sending_kb(meeting),
        )
    except Exception as e:
        return await query.answer(f"Error: {e}", show_alert=True)

    # TODO LATER:
    #       - for the students who want notifications

    await dialog_manager.switch_to(state=MeetingStates.info, show_mode=ShowMode.DELETE_AND_SEND)


def _adjust_duration(meeting: Meeting):
    if not meeting.date:
        raise ValueError("No meeting.date")
    date_obj = datetime.fromtimestamp(meeting.date)
    real_duration = datetime.now() - date_obj
    meeting.duration = int(real_duration.total_seconds())
