from aiogram_dialog import DialogManager

from src.bot.extended_dialog_manager import extend
from src.bot.user_errors import *
from src.bot.utils import *
from src.db.repositories import meetings_repo, tutors_repo
from src.domain.models import MeetingStatus, Tutor


async def remove_tutor(tutor: Tutor, manager: DialogManager):
    manager = extend(manager)

    meetings = []
    meetings.extend(await meetings_repo.list(status=MeetingStatus.CREATED, tutor_id=tutor.id))
    meetings.extend(await meetings_repo.list(status=MeetingStatus.ANNOUNCED, tutor_id=tutor.id))
    meetings.extend(await meetings_repo.list(status=MeetingStatus.CONDUCTING, tutor_id=tutor.id))
    if len(meetings) > 0:
        raise TutorStillAssigned()

    await tutors_repo.remove(tutor=tutor)
    await manager.state.update_data({"tutor": None})
    await send_to(tutor.tg_id, "You've been dismissed from being a tutor ⛄️")


async def add_tutor_from_shared_user(message: Message, manager: DialogManager):
    manager = extend(manager)
    if not message.users_shared:
        raise NoMessageUsersShared()
    shared_user = message.users_shared.users[0]
    if shared_user.username is None:
        raise NoSharedUserUsername()
    if await tutors_repo.exists(tg_id=shared_user.user_id):
        raise UserAlreadyTutor()
    tutor = await tutors_repo.create(
        tg_id=shared_user.user_id,
        username=shared_user.username,
        first_name=shared_user.first_name,
        last_name=shared_user.last_name,
    )
    await manager.state.set_tutor(tutor)
    await send_to(tutor.tg_id, "You've been chosen to be a tutor! 👨‍🏫\nUse /start to open the tutor menu")
