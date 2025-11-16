from datetime import datetime

from aiogram_dialog import DialogManager

from src.bot.filters import *
from src.domain.models import *

TEST_MEETINGS = [
    Meeting(status=CREATED, id=1, title="Prob&Stat Recap 3", date=1762983763, duration=3600),
    Meeting(
        status=CREATED,
        id=2,
        title="MathAn Recap 1",
        date=1762997763,
    ),
    Meeting(
        status=CREATED,
        id=3,
        title="Individual Maxim Pavlov",
        date=1762947763,
    ),
    Meeting(
        status=CREATED,
        id=4,
        title="OS PreFinal Preparation",
        date=1762947763,
    ),
    Meeting(
        status=CREATED,
        id=5,
        title="Optimization Last Recap",
    ),
]


async def meetings_list_getter(dialog_manager: DialogManager, **kwargs):
    return {"meetings_type": str(dialog_manager.dialog_data["meetings_type"]).capitalize(), "meetings": TEST_MEETINGS}


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
        "tutor": tutor.username if (tutor := data.get("tutor")) else None,
        "tutor_username": "@" + str(meeting.tutor_username) if meeting.tutor_username else "Not Assigned",
    }
