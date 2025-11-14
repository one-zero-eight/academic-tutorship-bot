import re
from types import ModuleType

from aiogram import Bot
from aiogram.types import Message
from aiogram_dialog import DialogManager


async def clear_messages(bot: Bot, dialog_manager: DialogManager):
    if to_delete := dialog_manager.dialog_data.pop("to_delete", None):
        to_delete: Message
        try:
            await bot.delete_message(to_delete.chat.id, to_delete.message_id)
        except Exception:
            pass


def get_windows(module: ModuleType):
    """
    Returns a dictionary of variables from the given module that match the pattern:
    admin_.*_ww (i.e., start with 'admin_', anything in between, and end with '_ww')
    """
    pattern = re.compile(r"^admin_.*_ww$")
    result = []
    for name, value in vars(module).items():
        if pattern.match(name):
            result.append(value)
    return result
