from aiogram.types import Message
from aiogram_dialog import DialogManager

from src.bot.dialog_extension import extend_dialog
from src.bot.user_errors import *
from src.bot.utils import *
from src.db.repositories import meeting_repo, student_repo, tutor_repo
from src.domain.models import MeetingStatus, Tutor


async def remove_tutor(tutor: Tutor, manager: DialogManager):
    manager = extend_dialog(manager)

    meetings = await meeting_repo.get_list((MeetingStatus.CREATED, MeetingStatus.CONDUCTING), tutor_id=tutor.id)
    if len(meetings) > 0:
        raise TutorStillAssigned()

    await tutor_repo.remove(tutor)
    await manager.state.update_data({"tutor": None})
    await send_to(tutor.telegram_id, "You've been dismissed from being a tutor ⛄️")


async def add_tutor_from_shared_user(message: Message, manager: DialogManager):
    manager = extend_dialog(manager)
    if not message.users_shared:
        raise NoMessageUsersShared()
    shared_user = message.users_shared.users[0]
    if shared_user.username is None:
        raise NoSharedUserUsername()
    if await tutor_repo.exists(telegram_id=shared_user.user_id):
        raise UserAlreadyTutor()
    if not (await student_repo.exists(shared_user.user_id)):
        raise ValueError("User is not authorized in the bot")
    student = await student_repo.get(shared_user.user_id)
    tutor = await tutor_repo.create(student.id)
    await manager.state.set_tutor(tutor)
    await send_to(tutor.telegram_id, "You've been chosen to be a tutor! 👨‍🏫\nUse /start to open the tutor menu")
