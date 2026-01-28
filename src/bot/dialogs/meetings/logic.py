from datetime import datetime

from aiogram.types import Message
from aiogram_dialog import DialogManager

from src.bot.dialog_extension import extend_dialog
from src.bot.scheduling import *
from src.bot.user_errors import *
from src.bot.utils import *
from src.db.repositories import meetings_repo
from src.domain.models import Meeting


async def announce_meeting(query: CallbackQuery, manager: DialogManager):
    manager = extend_dialog(manager)
    async with manager.state.sync_meeting() as meeting:
        tutor = meeting.tutor
        if not tutor:
            raise ValueError("No tutor")
        meeting.announce()
        await update_meeting_schedule(meeting)
        await meetings_repo.save(meeting)
        await send_to_admins_and_tutor(
            meeting,
            (
                f'A meeting was announced 📣\nTitle: "{meeting.title}"\nDate: {meeting.date_human}\nTutor: @{tutor.username}'
            ),
        )


async def create_meeting_with_title(message: Message, manager: DialogManager):
    manager = extend_dialog(manager)
    if not message.text:
        raise NoMessageText()
    new_meeting = await meetings_repo.create(title=message.text)
    await manager.state.set_meeting(new_meeting)


async def delete_meeting(query: CallbackQuery, manager: DialogManager):
    manager = extend_dialog(manager)
    meeting = await manager.state.get_meeting()
    await meetings_repo.remove(meeting=meeting)
    await wipe_meeting_schedule(meeting)
    await manager.state.update_data({"meeting": None})
    await send_to_admins_and_tutor(
        meeting, f'A meeting was deleted 🗑️\nTitle: "{meeting.title}"\nDate: {meeting.date_human}\n'
    )


async def finish_meeting(manager: DialogManager):
    manager = extend_dialog(manager)
    async with manager.state.sync_meeting() as meeting:
        meeting.finish()
        _adjust_duration(meeting)
        await meetings_repo.save(meeting)
        await wipe_meeting_schedule(meeting)
        await send_to_admins(
            meeting,
            text=(
                f'Meeting "{meeting.title}" finished ☑️ \n'
                f"Date: {meeting.date_human}\n"
                f"Duration: {meeting.duration_human}\n"
                f"Tutor: @{meeting.tutor.username if meeting.tutor else '---'}\n"
            ),
            skip_tutor=True,
        )
        await send_to_tutor(
            meeting,
            text=(
                f'Meeting "{meeting.title}" finished ☑️ \n'
                f"Date: {meeting.date_human}\n"
                f"Duration: {meeting.duration_human}\n"
                f"Tutor: @{meeting.tutor.username if meeting.tutor else '---'}\n"
                "\nSend an Attendance File to close the Meeting!"
            ),
            reply_markup=create_attendance_sending_kb(meeting),
        )


def _adjust_duration(meeting: Meeting):
    if not meeting.date:
        raise ValueError("No meeting.date")
    date_obj = datetime.fromtimestamp(meeting.date)
    real_duration = datetime.now() - date_obj
    meeting.duration = int(real_duration.total_seconds())
