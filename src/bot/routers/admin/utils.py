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
