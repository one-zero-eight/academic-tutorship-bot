from aiogram import Bot
from aiogram.types import Chat
from aiogram_dialog import DialogManager


async def clear_messages(bot: Bot, dialog_manager: DialogManager, chat: Chat):
    if to_delete_id := dialog_manager.dialog_data.pop("to_delete_id", None):
        try:
            await bot.delete_message(chat.id, to_delete_id)
        except Exception as e:
            return print(f"clear_messages failed, due to {e}")
