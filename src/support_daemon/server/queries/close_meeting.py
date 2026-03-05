from src.db.repositories import meetings_repo

from .base import Query


class CloseMeeting(Query):
    name: str = "CloseMeeting"
    args_dict = {"id": None}

    def __init__(self, id: int):
        self.id = id

    async def run(self) -> str:
        meeting = await meetings_repo.get(id=self.id)
        meeting.close([])
        await meetings_repo.save(meeting)
        return f"Closed Meeting id={self.id} (with no attendance)"

    @classmethod
    def _prepare_args(cls, data: dict) -> dict:
        prepared = data.copy()
        prepared["id"] = int(data["id"]) if data.get("id") else None
        return prepared
