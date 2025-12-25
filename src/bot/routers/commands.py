from aiogram import Bot, Router, types
from aiogram.filters import Command, CommandStart, ExceptionTypeFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import BotCommandScopeChat
from aiogram_dialog import DialogManager, StartMode

from src.accounts_sdk import inh_accounts
from src.bot.exceptions import UnauthenticatedException
from src.bot.filters import StatusFilter
from src.bot.routers.admin import AdminStates
from src.bot.routers.authentication import AuthStates
from src.bot.routers.student import StudentStates
from src.config import settings
from src.domain.enums import UserStatus as US

router = Router(name="commands")


MATCHING_START_STATE = {
    US.student: StudentStates.start,
    # US.tutor: TutorStates.start,
    US.admin: AdminStates.start,
}


@router.message(CommandStart())
@router.error(ExceptionTypeFilter(UnauthenticatedException))
async def on_start(
    message: types.Message, state: FSMContext, dialog_manager: DialogManager, authenticated: bool, status: US
):
    if not authenticated:
        return await dialog_manager.start(AuthStates.bind_tg_inh)
    else:
        return await dialog_manager.start(MATCHING_START_STATE[status])


@router.message(Command("admin"), StatusFilter(US.admin))
async def enable_admin_mode(message: types.Message, bot: Bot, dialog_manager: DialogManager):
    text = "You are the Admin!"
    await message.answer(text)
    await bot.set_my_commands(
        settings.bot_commands
        or []
        + [
            types.BotCommand(command="admin", description="Enable admin mode"),
        ],
        scope=BotCommandScopeChat(chat_id=message.chat.id),
    )
    await dialog_manager.start(AdminStates.start, mode=StartMode.RESET_STACK)


@router.message(Command("admin"), ~StatusFilter(US.admin))
async def failed_enable_admin_mode(message: types.Message, bot: Bot):
    text = "You are not the Admin!"
    await message.answer(text)
    await bot.set_my_commands(
        settings.bot_commands or [],
        scope=BotCommandScopeChat(chat_id=message.chat.id),
    )


@router.message(Command("testapi"), StatusFilter(US.admin))
async def test_accounts_api(message: types.Message, dialog_manager: DialogManager):
    inh_user = await inh_accounts.get_user(telegram_id=message.chat.id)
    if inh_user is None:
        await message.answer("You're not found :(")
    else:
        await message.answer(f"Your inh id: {inh_user.id}")
