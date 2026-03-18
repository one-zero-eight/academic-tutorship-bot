from aiogram import Bot, Router, types
from aiogram.filters import Command, CommandStart, ExceptionTypeFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import BotCommandScopeChat
from aiogram_dialog import DialogManager, ShowMode, StartMode

from src.accounts_sdk import inh_accounts
from src.bot.dialog_extension import extend_dialog
from src.bot.dialogs.meetings import MeetingStates
from src.bot.dialogs.student_meetings import StudentMeetingStates
from src.bot.dialogs.tutors_profile import TutorProfileStates
from src.bot.exceptions import UnauthenticatedException
from src.bot.filters import EMAIL_ENTERED_FILTER, USER_AUTHENTICATED_FILTER, StatusFilter
from src.bot.routers.admin import AdminStates
from src.bot.routers.authentication import AuthStates
from src.bot.routers.student import StudentStates
from src.bot.routers.tutor import TutorStates
from src.config import settings
from src.db.repositories import meeting_repo, tutor_repo
from src.domain.models import UserStatus as US

router = Router(name="commands")


MATCHING_START_STATE = {
    US.student: StudentStates.start,
    US.tutor: TutorStates.start,
    US.admin: AdminStates.start,
}


def _extract_start_payload(message: types.Message) -> str | None:
    if not message.text:
        return None
    parts = message.text.split(maxsplit=1)
    if len(parts) != 2:
        return None
    payload = parts[1].strip()
    return payload or None


@router.message(CommandStart())
@router.error(ExceptionTypeFilter(UnauthenticatedException))
async def on_start(
    message: types.Message, state: FSMContext, dialog_manager: DialogManager, authenticated: bool, status: US
):
    if authenticated:
        manager = extend_dialog(dialog_manager)
        payload = _extract_start_payload(message)
        await dialog_manager.start(MATCHING_START_STATE[status], mode=StartMode.RESET_STACK)
        if payload and payload != "welcome":
            if payload.startswith("meeting_"):
                meeting_id_text = payload.removeprefix("meeting_")
                if meeting_id_text.isdigit():
                    meeting = await meeting_repo.get(int(meeting_id_text))
                    await manager.state.set_meeting(meeting)
                    target_state = MeetingStates.info if status in (US.tutor, US.admin) else StudentMeetingStates.info
                    return await manager.start(target_state, show_mode=ShowMode.DELETE_AND_SEND)
            if payload == "promoted_tutor":
                if await tutor_repo.exists(telegram_id=message.chat.id):
                    self_tutor = await tutor_repo.get(telegram_id=message.chat.id)
                    await manager.state.set_self_tutor(self_tutor)
                    return await manager.start(TutorProfileStates.profile_control, show_mode=ShowMode.DELETE_AND_SEND)
    if settings.mock_auth:
        # NOTE: Do nothing if using mock_auth, MockAutoAuthMiddleware handles everything
        return
    return await dialog_manager.start(AuthStates.bind_tg_inh, mode=StartMode.RESET_STACK)


@router.message(~USER_AUTHENTICATED_FILTER, EMAIL_ENTERED_FILTER)
async def on_email(message: types.Message, state: FSMContext):
    # NOTE: needed just for MockAutoAuthMiddleware to work
    pass


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
