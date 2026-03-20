from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager

from src.bot.dialog_extension import extend_dialog
from src.bot.logging_ import log_info, log_warning
from src.bot.user_errors import *
from src.bot.utils import *
from src.db.repositories import meeting_repo

from .states import *


async def on_meeting_selected(query: CallbackQuery, meeting, manager: DialogManager, item_id: str):
    manager = extend_dialog(manager)
    log_info("student_meeting.select.requested", user_id=query.from_user.id, meeting_id=item_id)
    try:
        meeting = await meeting_repo.get(int(item_id))
    except LookupError:
        log_warning("student_meeting.select.not_found", user_id=query.from_user.id, meeting_id=item_id)
        return await query.answer("Meeting not found", show_alert=True)
    await manager.state.set_meeting(meeting)
    log_info("student_meeting.select.succeeded", user_id=query.from_user.id, meeting_id=meeting.id)
    await manager.switch_to(StudentMeetingStates.info)
