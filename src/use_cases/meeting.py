"""
Use Cases to work with meeting

Handles database queries, integrity checks, sheduling and notifications
"""

from src.bot.utils import create_attendance_sending_kb, send_to_admins, send_to_admins_and_tutor, send_to_tutor
from src.db.repositories import meeting_repo, tutor_repo
from src.domain.models import Meeting
from src.scheduling.scheduling import update_meeting_schedule, wipe_meeting_schedule


async def update(
    meeting: Meeting,
    *,
    title: str | None = None,
    description: str | None = None,
    room: str | None = None,
    date: int | None = None,
    duration: int | None = None,
):
    WORTH_NOTIFICATION = ["room", "datetime"]
    args = {"title": title, "description": description, "room": room, "datetime": date, "duration": duration}
    for key, value in args.items():
        if key is not None:
            setattr(meeting, key, value)
            if key == "date":
                await update_meeting_schedule(meeting)
            if key in WORTH_NOTIFICATION:
                # TODO: NOTIFICATION HERE
                pass
    await meeting_repo.update(meeting)


# async def assign_tutor(
#         meeting: Meeting,
#         tutor: Tutor
# ):
#     if (old_tutor_id := meeting.tutor_id) and old_tutor_id != tutor.id:
#         # TODO: notify tutor unassigned
#         # await notify_tutor_unassigned(old_tutor, meeting, manager)
#     new_tutor = await tutor_repo.get(telegram_id=shared_user.user_id)
#     meeting.assign_tutor(new_tutor)
#     await meeting_repo.update(meeting)
#     await notify_tutor_assigned(new_tutor, meeting, manager)


async def announce(meeting: Meeting):
    if not meeting.tutor_id:
        raise ValueError("No tutor")
    meeting.announce()
    await update_meeting_schedule(meeting)
    await meeting_repo.update(meeting, ["status"])
    tutor = await tutor_repo.get(id=meeting.tutor_id)
    await send_to_admins_and_tutor(  # TODO: move that to NotificationManager
        meeting,
        (f'A meeting was announced 📣\nTitle: "{meeting.title}"\nDate: {meeting.datetime_}\nTutor: @{tutor.username}'),
    )


async def finish(meeting: Meeting):
    meeting.finish()
    meeting.adjust_duration_to_now()
    await meeting_repo.update(meeting)
    await wipe_meeting_schedule(meeting)
    tutor = await tutor_repo.get(id=meeting.tutor_id)
    await send_to_admins(  # TODO: move that to NotificationManager
        meeting,
        text=(
            f'Meeting "{meeting.title}" finished ☑️ \n'
            f"Date: {meeting.datetime_}\n"
            f"Duration: {meeting.duration_human}\n"
            f"Tutor: @{tutor.username if tutor else '---'}\n"
        ),
        skip_tutor=True,
    )
    await send_to_tutor(  # TODO: move that to NotificationManager
        meeting,
        text=(
            f'Meeting "{meeting.title}" finished ☑️ \n'
            f"Date: {meeting.datetime_}\n"
            f"Duration: {meeting.duration_human}\n"
            f"Tutor: @{tutor.username if tutor else '---'}\n"
            "\nSend an Attendance File to close the Meeting!"
        ),
        reply_markup=create_attendance_sending_kb(meeting),
    )


async def delete(meeting: Meeting):
    await meeting_repo.remove(meeting.id)
    await wipe_meeting_schedule(meeting)
    await send_to_admins_and_tutor(  # TODO: move that to NotificationManager
        meeting, f'A meeting was deleted 🗑️\nTitle: "{meeting.title}"\nDate: {meeting.datetime_}\n'
    )
