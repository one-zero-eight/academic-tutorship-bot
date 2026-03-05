from datetime import datetime, timedelta

from apscheduler.triggers.date import DateTrigger

from src.bot.dto import *
from src.bot.utils import *
from src.db.repositories import meetings_repo

from .scheduler import scheduler


async def update_meeting_schedule(meeting: Meeting):
    if meeting.date and meeting.status < MeetingStatus.CONDUCTING:
        conduct_date = datetime.fromtimestamp(meeting.date)
        scheduler.add_job(
            trigger=DateTrigger(conduct_date),
            func=_job_meeting_conduct,
            args=[meeting.id],
            id=f"conduct_meeting_{meeting.id}",
            replace_existing=True,
            misfire_grace_time=None,  # always finish the task after restart
        )
        print(f"Scheduled Conducting of Meeting [{meeting.id}] at {conduct_date}")

    if meeting.date and meeting.duration and meeting.status < MeetingStatus.FINISHED:
        conduct_date = datetime.fromtimestamp(meeting.date)
        finish_date = conduct_date + timedelta(seconds=meeting.duration)
        scheduler.add_job(
            trigger=DateTrigger(finish_date),
            func=_job_meeting_finish,
            args=[meeting.id],
            id=f"finish_meeting_{meeting.id}",
            replace_existing=True,
            misfire_grace_time=None,  # always finish the task after restart
        )
        print(f"Scheduled Finishing of Meeting [{meeting.id}] at {finish_date}")


async def wipe_meeting_schedule(meeting: Meeting):
    possible_job_ids = [
        f"conduct_meeting_{meeting.id}",
        f"finish_meeting_{meeting.id}",
    ]

    for job_id in possible_job_ids:
        try:
            scheduler.remove_job(job_id)
        except Exception as e:
            print(f'Scheduler could not remove job "{job_id}", {e}')  # TODO: logging


async def _job_meeting_conduct(meeting_id: int):
    meeting = await meetings_repo.get(id=meeting_id)
    if not meeting:
        print("error in _job_meeting_conduct: no meeting")
        return  # TODO: proper error handeling
    try:
        meeting.conduct()
        await meetings_repo.save(meeting)
        print(f"Meeting [{meeting.id}] started conducting")
        await send_to_admins_and_tutor(
            meeting,
            text=(
                f'It is time to conduct "{meeting.title}" ⚡️\n'
                f'Date: {meeting.date_human}\n'
                f'Duration: {meeting.duration_human}\n'
                f'Tutor: @{meeting.tutor.username if meeting.tutor else "---"}\n'
            ),
        )

    except Exception as e:
        print(f"error in _job_meeting_conduct: {e}")
        return  # TODO: proper error handeling


async def _job_meeting_finish(meeting_id: int):
    meeting = await meetings_repo.get(id=meeting_id)
    if not meeting:
        print("error in _job_meeting_finish: no meeting")
        return  # TODO: proper error handeling
    try:
        meeting.finish()
        await meetings_repo.save(meeting)
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
        print(f"error in _job_meeting_finish: {e}")
        return  # TODO: proper error handeling
