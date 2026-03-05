from datetime import datetime

from src.db.repositories import meetings_repo, tutors_repo

from .base import Query


class UpdateMeeting(Query):
    name: str = "UpdateMeeting"
    args_dict = {
        "id": None,
        "title": None,
        "duration": None,
        "date": None,
        "room": None,
        "description": None,
        "tutor_id": None,
        "tutor_tg_id": None,
    }

    def __init__(
        self,
        id: int,
        title: str | None = None,
        duration: int | None = None,
        date: int | None = None,
        room: str | None = None,
        description: str | None = None,
        tutor_id: int | None = None,
        tutor_tg_id: int | None = None,
    ):
        self.id = id
        self.attrs = {
            "title": title,
            "duration": duration,
            "date": date,
            "room": room,
            "description": description,
        }
        self.tutor_id = tutor_id
        self.tutor_tg_id = tutor_tg_id

    async def run(self) -> str:
        meeting = await meetings_repo.get(id=self.id)
        for key, value in self.attrs.items():
            if value is not None:
                setattr(meeting, key, value)
        if self.tutor_id or self.tutor_tg_id:
            tutor = await tutors_repo.get(id=self.tutor_id, tg_id=self.tutor_tg_id)
            meeting.assign_tutor(tutor)
        await meetings_repo.save(meeting)
        return "Updated" + meeting.__repr__()

    @classmethod
    def _prepare_args(cls, data: dict) -> dict:
        prepared = data.copy()
        if not prepared["id"]:
            raise ValueError("meeting id must be specified")
        prepared["id"] = int(data["id"])
        prepared["date"] = cls.__prepare_date(data)
        prepared["duration"] = int(data["duration"]) if data.get("duration") else None
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
