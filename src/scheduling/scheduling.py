from datetime import datetime, timedelta

from apscheduler.triggers.date import DateTrigger

from src.bot.logging_ import logger
from src.bot.utils import *
from src.db.repositories import meeting_repo
from src.domain.models import MeetingStatus
from src.notifications import notification_manager

from .scheduler import scheduler


def meeting_job_ids(meeting_id: int) -> list[str]:
    return [
        f"remind_24h_meeting_{meeting_id}",
        f"remind_1h_meeting_{meeting_id}",
        f"conduct_meeting_{meeting_id}",
        f"finish_meeting_{meeting_id}",
    ]


async def update_meeting_schedule(meeting: Meeting):
    # rescheduling is authoritative: jobs that no longer apply must not survive
    await wipe_meeting_schedule(meeting)
    if meeting.status < MeetingStatus.ANNOUNCED:
        return  # schedule only when announced
    if meeting.datetime_ and meeting.status < MeetingStatus.CONDUCTING:
        conduct_date = meeting.datetime_
        now = datetime.now(conduct_date.tzinfo)

        reminders = {
            "24h": conduct_date - timedelta(hours=24),
            "1h": conduct_date - timedelta(hours=1),
        }
        for reminder_kind, reminder_date in reminders.items():
            if reminder_date <= now:
                continue
            scheduler.add_job(
                trigger=DateTrigger(reminder_date),
                func=_job_meeting_reminder,
                args=[meeting.id, reminder_kind],
                id=f"remind_{reminder_kind}_meeting_{meeting.id}",
                replace_existing=True,
                misfire_grace_time=None,  # always finish the task after restart
            )
            logger.info(f"Scheduled Meeting [{meeting.id}] reminder ({reminder_kind}) at {reminder_date}")

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
    for job_id in meeting_job_ids(meeting.id):
        if scheduler.get_job(job_id) is None:
            continue
        try:
            scheduler.remove_job(job_id)
        except Exception as e:
            logger.info(f'Scheduler could not remove job "{job_id}", {e}')


async def restore_meeting_schedules():
    meetings = await meeting_repo.get_list((MeetingStatus.ANNOUNCED, MeetingStatus.FINISHED))
    for meeting in meetings:
        await update_meeting_schedule(meeting)
    logger.info(f"Restored schedules for {len(meetings)} meetings")


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


async def _job_meeting_reminder(meeting_id: int, reminder_kind: str):
    meeting = await meeting_repo.get(meeting_id)
    if not meeting:
        logger.warning("error in _job_meeting_reminder: no meeting")
        return
    if meeting.status != MeetingStatus.ANNOUNCED:
        logger.info(f"Skipped reminder for Meeting [{meeting.id}] because status is {meeting.status.name}")
        return
    try:
        await notification_manager.send_meeting_reminder(meeting, reminder_kind=reminder_kind)
        logger.info(f"Meeting [{meeting.id}] reminder sent ({reminder_kind})")
    except Exception as e:
        logger.error(f"error in _job_meeting_reminder: {e}")
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
