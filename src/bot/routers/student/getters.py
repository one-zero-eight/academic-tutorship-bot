from aiogram.types import Chat
from aiogram_dialog import DialogManager


async def start_getter(dialog_manager: DialogManager, **kwargs):
    chat: Chat = kwargs["event_chat"]
    return {"first_name": chat.first_name}
