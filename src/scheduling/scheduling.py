from datetime import timedelta

from apscheduler.triggers.date import DateTrigger

from src.bot.logging_ import logger
from src.bot.utils import *
from src.db.repositories import meeting_repo
from src.domain.models import MeetingStatus
from src.notifications import notification_manager

from .scheduler import scheduler


async def update_meeting_schedule(meeting: Meeting):
    if meeting.status < MeetingStatus.ANNOUNCED:
        return  # schedule only when announced
    if meeting.datetime_ and meeting.status < MeetingStatus.CONDUCTING:
        conduct_date = meeting.datetime_
        scheduler.add_job(
            trigger=DateTrigger(conduct_date),
            func=_job_meeting_conduct,
            args=[meeting.id],
            id=f"conduct_meeting_{meeting.id}",
            replace_existing=True,
            misfire_grace_time=None,  # always finish the task after restart
        )
        logger.info(f"Scheduled Conducting of Meeting [{meeting.id}] at {conduct_date}")

    if meeting.datetime_ and meeting.duration and meeting.status < MeetingStatus.FINISHED:
        conduct_date = meeting.datetime_
        finish_date = conduct_date + timedelta(seconds=meeting.duration)
        scheduler.add_job(
            trigger=DateTrigger(finish_date),
            func=_job_meeting_finish,
            args=[meeting.id],
            id=f"finish_meeting_{meeting.id}",
            replace_existing=True,
            misfire_grace_time=None,  # always finish the task after restart
        )
        logger.info(f"Scheduled Finishing of Meeting [{meeting.id}] at {finish_date}")


async def wipe_meeting_schedule(meeting: Meeting):
    possible_job_ids = [
        f"conduct_meeting_{meeting.id}",
        f"finish_meeting_{meeting.id}",
    ]

    for job_id in possible_job_ids:
        try:
            scheduler.remove_job(job_id)
        except Exception as e:
            logger.info(f'Scheduler could not remove job "{job_id}", {e}')


async def _job_meeting_conduct(meeting_id: int):
    meeting = await meeting_repo.get(meeting_id)
    if not meeting:
        logger.warning("error in _job_meeting_conduct: no meeting")
    try:
        meeting.conduct()
        await meeting_repo.update(meeting, ["status"])
        logger.info(f"Meeting [{meeting.id}] started")
        await notification_manager.send_meeting_started(meeting)

    except Exception as e:
        logger.error(f"error in _job_meeting_conduct: {e}")
        return  # TODO: proper error handeling


async def _job_meeting_finish(meeting_id: int):
    meeting = await meeting_repo.get(id=meeting_id)
    if not meeting:
        logger.error("error in _job_meeting_finish: no meeting")
        return  # TODO: proper error handeling
    try:
        meeting.finish()
        await meeting_repo.update(meeting, ["status"])
        logger.info(f"Meeting [{meeting.id}] finished")
        await notification_manager.send_meeting_finished(meeting)
    except Exception as e:
        logger.error(f"error in _job_meeting_finish: {e}")
        return  # TODO: proper error handeling
