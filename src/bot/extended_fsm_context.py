from contextlib import asynccontextmanager

from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.bot.dto import *


class ExtendedFSMContext(FSMContext):
    @staticmethod
    def wrap(fsm_context: FSMContext) -> "ExtendedFSMContext":
        return ExtendedFSMContext(storage=fsm_context.storage, key=fsm_context.key)

    async def get_meeting(self) -> Meeting:
        if not (meeting := dto_to_meeting(await self.get_value("meeting"))):
            raise ValueError("No meeting in state storage")
        return meeting

    async def set_meeting(self, meeting: Meeting):
        await self.update_data({"meeting": meeting_to_dto(meeting)})

    @asynccontextmanager
    async def sync_meeting(self):
        try:
            meeting = await self.get_meeting()
            yield meeting
        finally:
            await self.set_meeting(meeting)

    async def get_tutor(self) -> Tutor:
        if not (tutor := dto_to_tutor(await self.get_value("tutor"))):
            raise ValueError("No tutor in state storage")
        return tutor

    async def set_tutor(self, tutor: Tutor):
        await self.update_data({"tutor": tutor_to_dto(tutor)})

    @asynccontextmanager
    async def sync_tutor(self):
        try:
            tutor = await self.get_tutor()
            yield tutor
        finally:
            await self.set_tutor(tutor)

    async def get_to_delete_list(self) -> list[int]:
        return await self.get_value("to_delete_list", [])

    async def set_to_delete_list(self, to_delete_list: list[int]):
        await self.update_data({"to_delete_list": to_delete_list})

    async def add_to_delete(self, message: Message):
        to_delete_list = await self.get_to_delete_list()
        to_delete_list.append(message.message_id)
        print("UPDATED TO DELETE:", to_delete_list)
        await self.set_to_delete_list(to_delete_list)


def extend(fsm_context: FSMContext) -> ExtendedFSMContext:
    if not isinstance(fsm_context, ExtendedFSMContext):
        fsm_context = ExtendedFSMContext.wrap(fsm_context)
    return fsm_context
