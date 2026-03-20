from src.bot.logging_ import log_error, log_info, log_warning
from src.bot.user_errors import *
from src.db.repositories import meeting_repo, student_repo, tutor_repo
from src.domain.models import MeetingStatus, Tutor
from src.notifications import notification_manager


async def remove_tutor(tutor: Tutor):
    meetings = await meeting_repo.get_list((MeetingStatus.CREATED, MeetingStatus.CONDUCTING), tutor_id=tutor.id)
    if len(meetings) > 0:
        log_warning("tutor.logic.remove.blocked_assigned", tutor_id=tutor.id, meetings_count=len(meetings))
        raise TutorStillAssigned()
    try:
        await tutor_repo.remove(tutor)
        await notification_manager.send_tutor_dismissed(tutor)
    except Exception as e:
        log_error("tutor.logic.remove.failed", tutor_id=tutor.id, reason=str(e))
        raise
    log_info("tutor.logic.remove.persisted_notified", tutor_id=tutor.id)


async def add_tutor_from_telegram_id(telegram_id: int) -> Tutor:
    if await tutor_repo.exists(telegram_id=telegram_id):
        log_warning("tutor.logic.add.blocked", telegram_id=telegram_id, reason="already_tutor")
        raise UserAlreadyTutor()
    if not (await student_repo.exists(telegram_id=telegram_id)):
        log_warning("tutor.logic.add.blocked", telegram_id=telegram_id, reason="not_authorized")
        raise ValueError("User is not authorized in the bot")
    try:
        student = await student_repo.get(telegram_id)
        tutor = await tutor_repo.create(student.id)
        await notification_manager.send_tutor_promoted(tutor)
    except Exception as e:
        log_error("tutor.logic.add.failed", telegram_id=telegram_id, reason=str(e))
        raise
    log_info("tutor.logic.add.persisted_notified", telegram_id=telegram_id, tutor_id=tutor.id)
    return tutor
