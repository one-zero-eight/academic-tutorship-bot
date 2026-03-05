from src.db.repositories import meetings_repo

from .base import Query


class DeleteMeeting(Query):
    name: str = "DeleteMeeting"
    args_dict = {"id": None}

    def __init__(self, id: int):
        self.id = id

    async def run(self) -> str:
        await meetings_repo.remove(id=self.id)
        return f"Removed Meeting id={self.id}"

    @classmethod
    def _prepare_args(cls, data: dict) -> dict:
        prepared = data.copy()
        prepared["id"] = int(data["id"]) if data.get("id") else None
        return prepared
