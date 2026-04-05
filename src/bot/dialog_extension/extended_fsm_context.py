from contextlib import asynccontextmanager
from datetime import datetime

from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.domain.models import Meeting, Student, Tutor

MEETING_KEY = "meeting"
TUTOR_KEY = "tutor"
SELF_STUDENT_KEY = "self_student"
SELF_TUTOR_KEY = "self_tutor"
TO_DELETE_LIST_KEY = "to_delete_list"


class ExtendedFSMContext(FSMContext):
    @staticmethod
    def wrap(fsm_context: FSMContext) -> "ExtendedFSMContext":
        return ExtendedFSMContext(storage=fsm_context.storage, key=fsm_context.key)

    # -- Student --

    async def get_self_student(self) -> Student:
        if not (self_student := await self.get_value(SELF_STUDENT_KEY)):
            raise ValueError("No self_student in state storage")
        return Student.model_validate(self_student)

    async def set_self_student(self, self_student: Student):
        data = self_student.model_dump()
        await self.update_data({SELF_STUDENT_KEY: data})

    @asynccontextmanager
    async def sync_self_student(self):
        try:
            self_student = await self.get_self_student()
            yield self_student
            await self.set_self_student(self_student)
        finally:
            pass

    # -- Meeting --

    async def get_meeting(self) -> Meeting:
        if not (meeting := await self.get_value(MEETING_KEY)):
            raise ValueError("No meeting in state storage")
        meeting["datetime"] = self.__deserialize_datetime(meeting["datetime"])
        meeting["created_at"] = self.__deserialize_datetime(meeting["created_at"])
        return Meeting.model_validate(meeting)

    async def set_meeting(self, meeting: Meeting):
        data = meeting.model_dump(by_alias=True)
        data["datetime"] = self.__serialize_datetime(data["datetime"])
        data["created_at"] = self.__serialize_datetime(data["created_at"])
        await self.update_data({MEETING_KEY: data})

    def __serialize_datetime(self, dt: datetime | None) -> float | None:
        return dt.timestamp() if dt else None

    def __deserialize_datetime(self, dt: float | None) -> datetime | None:
        return datetime.fromtimestamp(dt) if dt else None

    @asynccontextmanager
    async def sync_meeting(self):
        try:
            meeting = await self.get_meeting()
            yield meeting
            await self.set_meeting(meeting)
        finally:
            pass

    # -- Tutor --

    async def get_tutor(self) -> Tutor:
        if not (tutor := await self.get_value(TUTOR_KEY)):
            raise ValueError("No tutor in state storage")
        return Tutor.model_validate(tutor)

    async def set_tutor(self, tutor: Tutor):
        await self.update_data({TUTOR_KEY: tutor.model_dump()})

    @asynccontextmanager
    async def sync_tutor(self):
        try:
            tutor = await self.get_tutor()
            yield tutor
            await self.set_tutor(tutor)
        finally:
            pass

    # -- Self Tutor --

    async def get_self_tutor(self) -> Tutor:
        if not (self_tutor := await self.get_value(SELF_TUTOR_KEY)):
            raise ValueError("No self_tutor in state storage")
        return Tutor.model_validate(self_tutor)

    async def set_self_tutor(self, tutor: Tutor):
        await self.update_data({SELF_TUTOR_KEY: tutor.model_dump()})

    @asynccontextmanager
    async def sync_self_tutor(self):
        try:
            self_tutor = await self.get_self_tutor()
            yield self_tutor
            await self.set_self_tutor(self_tutor)
        finally:
            pass

    # -- Misc --

    async def get_to_delete_list(self) -> list[int]:
        return await self.get_value(TO_DELETE_LIST_KEY, [])

    async def set_to_delete_list(self, to_delete_list: list[int]):
        await self.update_data({TO_DELETE_LIST_KEY: to_delete_list})

    async def add_to_delete(self, message: Message):
        to_delete_list = await self.get_to_delete_list()
        to_delete_list.append(message.message_id)
        await self.set_to_delete_list(to_delete_list)


def extend_fsm_context(fsm_context: FSMContext) -> ExtendedFSMContext:
    if not isinstance(fsm_context, ExtendedFSMContext):
        fsm_context = ExtendedFSMContext.wrap(fsm_context)
    return fsm_context
