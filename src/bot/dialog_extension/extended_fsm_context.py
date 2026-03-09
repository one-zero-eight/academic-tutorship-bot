from contextlib import asynccontextmanager
from datetime import datetime

from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.domain.models import Meeting, Tutor


class ExtendedFSMContext(FSMContext):
    @staticmethod
    def wrap(fsm_context: FSMContext) -> "ExtendedFSMContext":
        return ExtendedFSMContext(storage=fsm_context.storage, key=fsm_context.key)

    # -- Meeting --

    async def get_meeting(self) -> Meeting:
        if not (meeting := await self.get_value("meeting")):
            raise ValueError("No meeting in state storage")
        meeting["datetime"] = self.__deserialize_datetime(meeting["datetime"])
        meeting["created_at"] = self.__deserialize_datetime(meeting["created_at"])
        return Meeting(**meeting)

    async def set_meeting(self, meeting: Meeting):
        data = meeting.model_dump(by_alias=True)
        print(data)
        data["datetime"] = self.__serialize_datetime(data["datetime"])
        data["created_at"] = self.__serialize_datetime(data["created_at"])
        await self.update_data({"meeting": data})

    def __serialize_datetime(self, dt: datetime | None) -> float | None:
        return dt.timestamp() if dt else None

    def __deserialize_datetime(self, dt: float | None) -> datetime | None:
        return datetime.fromtimestamp(dt) if dt else None

    @asynccontextmanager
    async def sync_meeting(self):
        try:
            meeting = await self.get_meeting()
            yield meeting
        finally:
            await self.set_meeting(meeting)

    # -- Tutor --

    async def get_tutor(self) -> Tutor:
        if not (tutor := await self.get_value("tutor")):
            raise ValueError("No tutor in state storage")
        return Tutor(**tutor)

    async def set_tutor(self, tutor: Tutor):
        await self.update_data({"tutor": tutor.model_dump()})

    @asynccontextmanager
    async def sync_tutor(self):
        try:
            tutor = await self.get_tutor()
            yield tutor
        finally:
            await self.set_tutor(tutor)

    # -- Self Tutor --

    async def get_self_tutor(self) -> Tutor:
        if not (tutor := await self.get_value("self_tutor")):
            raise ValueError("No self_tutor in state storage")
        return Tutor(**tutor)

    async def set_self_tutor(self, tutor: Tutor):
        await self.update_data({"self_tutor": tutor.model_dump()})

    @asynccontextmanager
    async def sync_self_tutor(self):
        try:
            tutor = await self.get_self_tutor()
            yield tutor
        finally:
            await self.set_self_tutor(tutor)

    # -- Misc --

    async def get_to_delete_list(self) -> list[int]:
        return await self.get_value("to_delete_list", [])

    async def set_to_delete_list(self, to_delete_list: list[int]):
        await self.update_data({"to_delete_list": to_delete_list})

    async def add_to_delete(self, message: Message):
        to_delete_list = await self.get_to_delete_list()
        to_delete_list.append(message.message_id)
        await self.set_to_delete_list(to_delete_list)


def extend_fsm_context(fsm_context: FSMContext) -> ExtendedFSMContext:
    if not isinstance(fsm_context, ExtendedFSMContext):
        fsm_context = ExtendedFSMContext.wrap(fsm_context)
    return fsm_context
