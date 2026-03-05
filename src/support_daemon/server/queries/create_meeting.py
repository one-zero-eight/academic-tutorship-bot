from datetime import datetime

from src.db.repositories import meetings_repo, tutors_repo

from .base import Query


class CreateMeeting(Query):
    name: str = "CreateMeeting"
    args_dict = {
        "title": None,
        "duration": 5400,
        "date": None,
        "room": None,
        "description": None,
        "tutor_id": None,
        "tutor_tg_id": None,
    }

    def __init__(
        self,
        title: str,
        duration: int = 5400,  # 01:30 in seconds
        date: int | None = None,
        room: str | None = None,
        description: str | None = None,
        tutor_id: int | None = None,
        tutor_tg_id: int | None = None,
    ):
        self.title = title
        self.duration = duration
        self.date = date
        self.room = room
        self.description = description
        self.tutor_id = tutor_id
        self.tutor_tg_id = tutor_tg_id

    async def run(self) -> str:
        meeting = await meetings_repo.create(title=self.title)
        meeting.duration = self.duration
        meeting.date = self.date
        meeting.room = self.room
        meeting.description = self.description
        if self.tutor_id or self.tutor_tg_id:
            tutor = await tutors_repo.get(id=self.tutor_id, tg_id=self.tutor_tg_id)
            meeting.assign_tutor(tutor)
        await meetings_repo.save(meeting)
        return meeting.__repr__()

    @classmethod
    def _prepare_args(cls, data: dict) -> dict:
        prepared = data.copy()
        prepared["duration"] = int(data["duration"])
        prepared["date"] = cls.__prepare_date(data)
        prepared["tutor_id"] = int(data["tutor_id"]) if data.get("tutor_id") else None
        prepared["tutor_tg_id"] = int(data["tutor_tg_id"]) if data.get("tutor_tg_id") else None
        return prepared

    @staticmethod
    def __prepare_date(data):
        date = data["date"]
        if date and isinstance(date, str):
            if date.isnumeric():
                return int(date)
            elif is_isoformat_date(date):
                return int(datetime.fromisoformat(date).timestamp())
        elif date is None:
            return date
        raise ValueError(f'Unknown date format "{date}"')


def is_isoformat_date(date_string):
    try:
        datetime.fromisoformat(date_string)
        return True
    except ValueError:
        return False
