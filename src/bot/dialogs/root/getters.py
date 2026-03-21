from aiogram.types import Chat
from aiogram_dialog import DialogManager

from src.bot.dialog_extension import extend_dialog
from src.bot.utils import user_status_getter
from src.db.repositories import student_repo


async def start_getter(dialog_manager: DialogManager, **kwargs):
    data = await user_status_getter(dialog_manager, **kwargs)
    chat: Chat = kwargs["event_chat"]
    return {**data, "first_name": chat.first_name}


async def student_settings_getter(dialog_manager: DialogManager, **kwargs):
    manager = extend_dialog(dialog_manager)
    student = await student_repo.get(manager.chat.id)
    relevant_disciplines = await student_repo.get_relevant_disciplines(manager.chat.id)
    return {
        "receive_notifications": "✅" if student.settings.receive_notifications else "❌",
        "relevant_disciplines": [disc.model_dump() for disc in relevant_disciplines],
    }
