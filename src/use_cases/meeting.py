"""
Use Cases to work with meeting

Handles database queries, integrity checks, sheduling and notifications
"""

from src.bot.utils import create_attendance_sending_kb, send_to_admins, send_to_admins_and_tutor, send_to_tutor
from src.db.repositories import meetings_repo
from src.domain.models import Meeting
from src.scheduling.scheduling import update_meeting_schedule, wipe_meeting_schedule


async def create(title: str) -> Meeting:
    new_meeting = await meetings_repo.create(title=title)
    return new_meeting


async def update(
    meeting: Meeting,
    title: str | None = None,
    description: str | None = None,
    room: str | None = None,
    date: int | None = None,
    duration: int | None = None,
):
    # TODO: Complete after NotificationManager done
    ...


async def announce(meeting: Meeting):
    tutor = meeting.tutor
    if not tutor:
        raise ValueError("No tutor")
    meeting.announce()
    await update_meeting_schedule(meeting)
    await meetings_repo.save(meeting)
    await send_to_admins_and_tutor(  # TODO: move that to NotificationManager
        meeting,
        (f'A meeting was announced 📣\nTitle: "{meeting.title}"\nDate: {meeting.date_human}\nTutor: @{tutor.username}'),
    )


async def finish(meeting: Meeting):
    meeting.finish()
    meeting.adjust_duration_to_now()
    await meetings_repo.save(meeting)
    await wipe_meeting_schedule(meeting)
    await send_to_admins(  # TODO: move that to NotificationManager
        meeting,
        text=(
            f'Meeting "{meeting.title}" finished ☑️ \n'
            f"Date: {meeting.date_human}\n"
            f"Duration: {meeting.duration_human}\n"
            f"Tutor: @{meeting.tutor.username if meeting.tutor else '---'}\n"
        ),
        skip_tutor=True,
    )
    await send_to_tutor(  # TODO: move that to NotificationManager
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


async def delete(meeting: Meeting):
    await meetings_repo.remove(meeting=meeting)
    await wipe_meeting_schedule(meeting)
    await send_to_admins_and_tutor(  # TODO: move that to NotificationManager
        meeting, f'A meeting was deleted 🗑️\nTitle: "{meeting.title}"\nDate: {meeting.date_human}\n'
    )
