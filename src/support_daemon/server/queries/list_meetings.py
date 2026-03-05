from src.db.repositories import meetings_repo, tutors_repo
from src.domain.models import MeetingStatus

from .base import Query


class ListMeetings(Query):
    name: str = "ListMeetings"
    args_dict = {
        "status": "CREATED",
        "tutor_id": None,
        "tutor_tg_id": None,
    }

    def __init__(
        self, status: MeetingStatus | None = None, tutor_id: int | None = None, tutor_tg_id: int | None = None
    ):
        self.status = status
        self.tutor_id = tutor_id
        self.tutor_tg_id = tutor_tg_id

    async def run(self) -> str:
        tutor_id = None
        if self.tutor_tg_id or self.tutor_id:
            tutor = await tutors_repo.get(id=self.tutor_id, tg_id=self.tutor_tg_id)
            tutor_id = tutor.id
        meetings = await meetings_repo.list(tutor_id=tutor_id, status=self.status)
        return "\n".join([m.__repr__() for m in meetings])

    @classmethod
    def _prepare_args(cls, data: dict) -> dict:
        prepared = data.copy()
        prepared["status"] = cls.__prepare_status(prepared)
        prepared["tutor_id"] = int(prepared["tutor_id"]) if prepared.get("tutor_id") else None
        prepared["tutor_tg_id"] = int(prepared["tutor_tg_id"]) if prepared.get("tutor_tg_id") else None
        return prepared

    @staticmethod
    def __prepare_status(data):
        status = data["status"]
        match status:
            case "CREATED":
                return MeetingStatus.CREATED
            case "ANNOUNCED":
                return MeetingStatus.ANNOUNCED
            case "CONDUCTING":
                return MeetingStatus.CONDUCTING
            case "FINISHED":
                return MeetingStatus.FINISHED
            case "CLOSED":
                return MeetingStatus.CLOSED
            case _:
                raise ValueError(f'Unknown status "{status}"')
