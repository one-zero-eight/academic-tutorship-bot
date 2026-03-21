from aiogram import Bot
from aiogram_dialog import DialogManager

from src.config import settings


async def start_getter(dialog_manager: DialogManager, **kwargs):
    bot: Bot = kwargs["bot"]
    bot_username = (await bot.get_me()).username
    if not settings.telegram_bind_url:
        raise Exception("No telegram_bind_url in settings")
    return {"binding_url": settings.telegram_bind_url + f"?bot={bot_username}"}
