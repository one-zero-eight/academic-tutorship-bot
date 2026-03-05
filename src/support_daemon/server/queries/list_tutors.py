from src.db.repositories import tutors_repo

from .base import Query


class ListTutors(Query):
    name: str = "ListTutors"
    args_dict = {
        "profiles": False,
    }

    def __init__(self, profiles: bool = False):
        self.profiles = profiles

    async def run(self) -> str:
        tutors = await tutors_repo.list(only_with_profiles=self.profiles)
        return "\n".join([t.__repr__() for t in tutors])

    @classmethod
    def _prepare_args(cls, data: dict) -> dict:
        prepared = data.copy()
        prepared["profiles"] = bool(data["profiles"])
        return prepared
