from src.db.repositories import meetings_repo

from .base import Query


class FinishMeeting(Query):
    name: str = "FinishMeeting"
    args_dict = {"id": None}

    def __init__(self, id: int):
        self.id = id

    async def run(self) -> str:
        meeting = await meetings_repo.get(id=self.id)
        meeting.finish()
        await meetings_repo.save(meeting)
        return f"Finished Meeting id={self.id}"

    @classmethod
    def _prepare_args(cls, data: dict) -> dict:
        prepared = data.copy()
        prepared["id"] = int(data["id"]) if data.get("id") else None
        return prepared
