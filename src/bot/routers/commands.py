from aiogram import Bot, Router, types
from aiogram.filters import Command, CommandStart
from aiogram.types import BotCommandScopeChat
from aiogram_dialog import DialogManager, StartMode

from src.bot.routers.admin import AdminStates
from src.config import settings

router = Router(name="commands")


@router.message(CommandStart())
@router.message(Command("admin"))
async def enable_admin_mode(message: types.Message, bot: Bot, dialog_manager: DialogManager):
    text = "You are the Admin!"
    await message.answer(text)
    await bot.set_my_commands(
        settings.bot_commands
        or []
        + [
            types.BotCommand(command="admin", description="Enable admin mode"),
        ],
        scope=BotCommandScopeChat(chat_id=message.from_user.id),
    )
    await dialog_manager.start(AdminStates.menu, mode=StartMode.RESET_STACK)
