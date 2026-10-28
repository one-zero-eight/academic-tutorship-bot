from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, ShowMode

from src.bot.custom_widgets.disciplines_control_list_text import DisciplinesControlListText
from src.bot.dialog_extension import extend_dialog, require_status
from src.bot.logging_ import log_info
from src.domain.models import UserStatus as US

from .getters import disciplines_getter

MAX_MESSAGE_LENGTH = 4095


@require_status(US.admin)
async def send_multimessage_disciplines_list(query: CallbackQuery, _, manager: DialogManager):
    log_info("admin.disciplines_control.send_multimessage_disciplines_list.requested", user_id=query.from_user.id)

    assert query.message
    manager = extend_dialog(manager)
    data = await disciplines_getter(manager)
    disciplines_list_text = await DisciplinesControlListText()._render_text(data, manager)

    message_ids_to_delete = []
    for part in disciplines_list_text.split("\n\n"):
        sent = await query.message.answer(part)
        message_ids_to_delete.append(sent.message_id)

    await manager.state.update_data({"message_ids_to_delete": message_ids_to_delete})

    log_info("admin.disciplines_control.send_multimessage_disciplines_list.done", user_id=query.from_user.id)


async def clear_multimessage_disciplines_list(query: CallbackQuery, _, manager: DialogManager):
    log_info("disciplines_control.clear_multimessage_disciplines_list.requested", user_id=query.from_user.id)

    manager = extend_dialog(manager)

    bot = manager.bot
    user_id = query.from_user.id
    message_ids_to_delete = await manager.state.get_value("message_ids_to_delete", [])

    if message_ids_to_delete:
        await bot.delete_messages(user_id, message_ids_to_delete)
    await manager.state.update_data({"message_ids_to_delete": []})

    log_info("disciplines_control.clear_multimessage_disciplines_list.done", user_id=query.from_user.id)


@require_status(US.admin)
async def update_multimessage_disciplines_list(query: CallbackQuery, _, manager: DialogManager):
    log_info("disciplines_control.update_multimessage_disciplines_list.requested", user_id=query.from_user.id)
    manager = extend_dialog(manager)
    await clear_multimessage_disciplines_list(query, _, manager)
    await send_multimessage_disciplines_list(query, _, manager)
    await manager.switch_to_current(show_mode=ShowMode.DELETE_AND_SEND)
    log_info("disciplines_control.update_multimessage_disciplines_list.done", user_id=query.from_user.id)
