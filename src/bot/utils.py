import re
from types import ModuleType

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import BotCommand, Chat, Message
from aiogram_dialog import DialogManager
from pydantic import TypeAdapter

commands_type_adapter = TypeAdapter(list[BotCommand])


def check_commands_equality(x: list[BotCommand], y: list[BotCommand]) -> bool:
    return commands_type_adapter.dump_json(x) == commands_type_adapter.dump_json(y)


def get_windows(module: ModuleType):
    """
    Returns a dictionary of variables from the given module that match the pattern:
    .*_ww (i.e., anything ending with '_ww')
    """
    pattern = re.compile(r"^.*_ww$")
    result = []
    for name, value in vars(module).items():
        if pattern.match(name):
            result.append(value)
    return result


def get_state(dialog_manager: DialogManager) -> FSMContext:
    # NOTE: the "state" key must always exist in middleware_data
    return dialog_manager.middleware_data["state"]


async def clear_messages(dialog_manager: DialogManager):
    """Delete tracked messages ("to_delete_id" in state)"""
    bot: Bot = dialog_manager.middleware_data["bot"]
    chat: Chat = dialog_manager.middleware_data["event_chat"]
    if to_delete_id := dialog_manager.dialog_data.pop("to_delete_id", None):
        try:
            await bot.delete_message(chat.id, to_delete_id)
        except Exception as e:
            return print(f"clear_messages failed, due to {e}")


async def track_message(message: Message, dialog_manager: DialogManager):
    """Track messages to delete later ("to_delete_id" in state)"""
    await get_state(dialog_manager).update_data({"to_delete_id": message.message_id})
