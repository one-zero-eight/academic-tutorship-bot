from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager

from src.bot.dialog_extension import extend_dialog
from src.bot.user_errors import NoMessageText
from src.use_cases import meeting as meeting_use_case


async def announce_meeting(query: CallbackQuery, manager: DialogManager):
    manager = extend_dialog(manager)
    async with manager.state.sync_meeting() as meeting:
        await meeting_use_case.announce(meeting)


async def create_meeting_with_title(message: Message, manager: DialogManager):
    manager = extend_dialog(manager)
    if not message.text:
        raise NoMessageText()
    new_meeting = await meeting_use_case.create(message.text)
    await manager.state.set_meeting(new_meeting)


async def delete_meeting(query: CallbackQuery, manager: DialogManager):
    manager = extend_dialog(manager)
    meeting = await manager.state.get_meeting()
    await meeting_use_case.delete(meeting)
    await manager.state.update_data({"meeting": None})


async def finish_meeting(manager: DialogManager):
    manager = extend_dialog(manager)
    async with manager.state.sync_meeting() as meeting:
        await meeting_use_case.finish(meeting)
