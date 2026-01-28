from datetime import date, datetime, time

from aiogram.types import InaccessibleMessage, SharedUser
from aiogram_dialog import DialogManager

from src.bot.extended_dialog_manager import extend
from src.bot.scheduling import *
from src.bot.user_errors import *
from src.bot.utils import *
from src.db.repositories import meetings_repo, tutors_repo
from src.domain.models import Meeting, MeetingStatus, Tutor

MAX_ROOM_LEN = 64


def extract_shared_user(message: Message | InaccessibleMessage | None) -> SharedUser:
    if not message:
        raise ValueError("No message")
    if isinstance(message, InaccessibleMessage):
        raise ValueError("Message Inaccessible")
    if not message.users_shared:
        raise NoMessageUsersShared()
    return message.users_shared.users[0]


async def notify_tutor_assigned(tutor: Tutor, meeting: Meeting, manager: DialogManager):
    manager = extend(manager)
    try:
        await manager.bot.send_message(
            text=(
                "You are assigned to a Meeting 👨‍🏫\n"
                f"Title: {meeting.title}\n"
                f"Date: {meeting.date_human}\n"
                "\n"
                "You can now see the Meeting in your meetings list"
            ),
            chat_id=tutor.tg_id,
        )
    except Exception as e:
        print(f"Could not send notification to [{tutor.tg_id}] @{tutor.username}, {e}")


async def notify_tutor_unassigned(tutor: Tutor, meeting: Meeting, manager: DialogManager):
    manager = extend(manager)
    try:
        await manager.bot.send_message(
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


async def update_meeting_title(message: Message, manager: DialogManager):
    manager = extend(manager)
    if not message.text:
        raise NoMessageText()
    async with manager.state.sync_meeting() as meeting:
        meeting.title = message.text
    await meetings_repo.save(meeting)


async def update_meeting_description(message: Message, manager: DialogManager):
    manager = extend(manager)
    if not message.text:
        raise NoMessageText()
    async with manager.state.sync_meeting() as meeting:
        meeting.description = message.text
    await meetings_repo.save(meeting)


async def update_meeting_tutor_shared_user(shared_user: SharedUser, manager: DialogManager):
    manager = extend(manager)
    async with manager.state.sync_meeting() as meeting:
        if old_tutor := meeting.tutor:
            await notify_tutor_unassigned(old_tutor, meeting, manager)
        new_tutor = await tutors_repo.get(tg_id=shared_user.user_id)
        meeting.assign_tutor(new_tutor)
        await meetings_repo.save(meeting)
        await notify_tutor_assigned(new_tutor, meeting, manager)


async def update_meeting_tutor_item_id(item_id: str, manager: DialogManager):
    manager = extend(manager)
    async with manager.state.sync_meeting() as meeting:
        if old_tutor := meeting.tutor:
            await notify_tutor_unassigned(old_tutor, meeting, manager)
        new_tutor = await tutors_repo.get(id=int(item_id))
        meeting.assign_tutor(new_tutor)
        await meetings_repo.save(meeting)
        await notify_tutor_assigned(new_tutor, meeting, manager)


def extract_time(message: Message) -> time:
    if not message.text:
        raise NoMessageText()
    return parse_time(message.text)


async def combine_meeting_date_time(selected_time: time, manager: DialogManager):
    manager = extend(manager)
    selected_date_str = await manager.state.get_value("selected_date")
    if not selected_date_str:
        raise ValueError("No date")
    selected_date = date.fromisoformat(selected_date_str)
    meeting_date = datetime.combine(selected_date, selected_time)
    if meeting_date < datetime.now():
        raise DateInPast()
    return meeting_date


async def update_meeting_date(meeting_date: datetime, manager: DialogManager):
    manager = extend(manager)
    async with manager.state.sync_meeting() as meeting:
        meeting.date = int(meeting_date.timestamp())
    await meetings_repo.save(meeting)
    if meeting.status > MeetingStatus.CREATED:
        await update_meeting_schedule(meeting)


async def warn_if_date_is_too_soon(meeting_date: datetime, message: Message):
    if (meeting_date - datetime.now()).days < 1:
        await message.answer(
            text=("Warning ⚠️\nThe meeting would be conducted in less than 24H\n"), reply_markup=DELETE_WARNING_KB
        )


async def update_meeting_duration(selected_time: time, manager: DialogManager):
    manager = extend(manager)
    async with manager.state.sync_meeting() as meeting:
        meeting.duration = selected_time.hour * 3600 + selected_time.minute * 60
    await meetings_repo.save(meeting)
    if meeting.status > MeetingStatus.CREATED:
        await update_meeting_schedule(meeting)


async def update_meeting_room(message: Message, manager: DialogManager):
    manager = extend(manager)
    if not message.text:
        raise NoMessageText()
    if len(message.text) > MAX_ROOM_LEN:
        raise RoomTooLong()
    async with manager.state.sync_meeting() as meeting:
        meeting.room = message.text
    await meetings_repo.save(meeting)
