from datetime import datetime

from aiogram_dialog import DialogManager

from src.bot.filters import *
from src.db.repositories import meetings_repo, tutors_repo
from src.domain.models import *


async def meetings_list_getter(dialog_manager: DialogManager, **kwargs):
    meetings_type = dialog_manager.dialog_data["meetings_type"]
    if meetings_type == "created":
        allowed_statuses = {MeetingStatus.CREATED}
    elif meetings_type == "announced":
        allowed_statuses = {MeetingStatus.ANNOUNCED, MeetingStatus.CONDUCTING, MeetingStatus.FINISHED}
    elif meetings_type == "closed":
        allowed_statuses = {MeetingStatus.CLOSED}
    else:
        allowed_statuses = set()

    meetings = []
    for status in allowed_statuses:
        meetings.extend(await meetings_repo.list(status=status))

    return {
        "meetings_type": meetings_type.capitalize(),
        "meetings": meetings,
    }


async def meeting_info_getter(dialog_manager: DialogManager, **kwargs):
    data = dialog_manager.dialog_data
    meeting: Meeting = data["meeting"]
    date_to_str = lambda x: datetime.fromtimestamp(x).strftime("%d.%m.%Y")  # noqa E731
    duration_to_str = lambda x: f"{x // 3600:02d}:{(x % 3600) // 60:02d}"  # noqa E731
    return {
        "title": meeting.title,
        "description": meeting.description,
        "date": date_to_str(meeting.date) if meeting.date else "--.--.----",
        "duration": duration_to_str(meeting.duration) if meeting.duration else "--:--",
        "tutor_username": meeting.tutor.username if meeting.tutor else None,
    }


async def meeting_info_with_tutors_getter(dialog_manager: DialogManager, **kwargs):
    data = dialog_manager.dialog_data
    meeting: Meeting = data["meeting"]
    date_to_str = lambda x: datetime.fromtimestamp(x).strftime("%d.%m.%Y")  # noqa E731
    duration_to_str = lambda x: f"{x // 3600:02d}:{(x % 3600) // 60:02d}"  # noqa E731
    tutors = await tutors_repo.list()
    return {
        "title": meeting.title,
        "description": meeting.description,
        "date": date_to_str(meeting.date) if meeting.date else "--.--.----",
        "duration": duration_to_str(meeting.duration) if meeting.duration else "--:--",
        "tutor_username": meeting.tutor.username if meeting.tutor else None,
        "tutors": list(enumerate(tutors)),
    }


async def tutors_list_getter(dialog_manager: DialogManager, **kwargs):
    tutors = await tutors_repo.list()
    return {
        "tutors": list(enumerate(tutors)),
    }


async def tutor_info_getter(dialog_manager: DialogManager, **kwargs):
    data = dialog_manager.dialog_data
    tutor: Tutor = data["tutor"]
    return {
        "id": tutor.id,
        "tg_id": tutor.tg_id,
        "username": tutor.username,
        "full_name": tutor.full_name,
    }
