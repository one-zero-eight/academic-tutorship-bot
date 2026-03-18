from src.bot.user_errors import *
from src.db.repositories import meeting_repo, student_repo, tutor_repo
from src.domain.models import MeetingStatus, Tutor
from src.notifications import notification_manager


async def remove_tutor(tutor: Tutor):
    meetings = await meeting_repo.get_list((MeetingStatus.CREATED, MeetingStatus.CONDUCTING), tutor_id=tutor.id)
    if len(meetings) > 0:
        raise TutorStillAssigned()
    await tutor_repo.remove(tutor)
    await notification_manager.send_tutor_dismissed(tutor)


async def add_tutor_from_telegram_id(telegram_id: int) -> Tutor:
    if await tutor_repo.exists(telegram_id=telegram_id):
        raise UserAlreadyTutor()
    if not (await student_repo.exists(telegram_id=telegram_id)):
        raise ValueError("User is not authorized in the bot")
    student = await student_repo.get(telegram_id)
    tutor = await tutor_repo.create(student.id)
    await notification_manager.send_tutor_promoted(tutor)
    return tutor
