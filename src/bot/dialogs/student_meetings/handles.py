from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager

from src.bot.dialog_extension import extend_dialog
from src.bot.dto import *
from src.bot.user_errors import *
from src.bot.utils import *
from src.db.repositories import meetings_repo

from .states import *


async def on_meeting_selected(query: CallbackQuery, meeting, manager: DialogManager, item_id: str):
    manager = extend_dialog(manager)
    meeting = await meetings_repo.get(id=int(item_id))
    await manager.state.set_meeting(meeting)
    await manager.switch_to(StudentMeetingStates.info)
