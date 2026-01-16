from typing import Literal

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Button

from src.bot.dto import *
from src.bot.utils import get_state
from src.db.repositories import meetings_repo

from .states import *


async def on_meeting_selected(query: CallbackQuery, meeting, dialog_manager: DialogManager, item_id: str):
    meeting = await meetings_repo.get(id=int(item_id))
    await get_state(dialog_manager).update_data({"meeting": meeting_to_dto(meeting)})
    await dialog_manager.switch_to(MeetingStates.info)


def open_meetings_list_of_type(type: Literal["created", "announced", "closed"]):
    """Higher order function, returns Awaitable that opens specified meetings list"""

    async def open_meetings_list(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
        await get_state(dialog_manager).update_data({"meetings_type": type})
        await dialog_manager.switch_to(MeetingStates.list)

    return open_meetings_list


async def open_meeting_create(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(MeetingStates.create)


async def get_new_title(message: Message, message_input, dialog_manager: DialogManager):
    if not message.text:
        raise ValueError("No message.text")  # noqa E701

    new_meeting = await meetings_repo.create(title=message.text)
    await get_state(dialog_manager).update_data({"meeting": meeting_to_dto(new_meeting)})
    await dialog_manager.switch_to(MeetingStates.info, show_mode=ShowMode.DELETE_AND_SEND)
    await message.delete()
