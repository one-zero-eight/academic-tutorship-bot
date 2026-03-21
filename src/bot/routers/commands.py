from aiogram import Router, types
from aiogram.filters import Command, CommandStart, ExceptionTypeFilter
from aiogram.fsm.context import FSMContext
from aiogram_dialog import DialogManager, ShowMode, StartMode

from src.accounts_sdk import inh_accounts
from src.bot.dialog_extension import extend_dialog
from src.bot.dialogs.authentication import AuthStates
from src.bot.dialogs.guide import GuideStates
from src.bot.dialogs.meetings import MeetingStates
from src.bot.dialogs.root import RootStates
from src.bot.dialogs.student_meetings import StudentMeetingStates
from src.bot.dialogs.tutors_profile import TutorProfileStates
from src.bot.exceptions import UnauthenticatedException
from src.bot.filters import EMAIL_ENTERED_FILTER, USER_AUTHENTICATED_FILTER, StatusFilter
from src.bot.logging_ import log_error, log_info, log_warning
from src.db.repositories import meeting_repo, tutor_repo
from src.domain.models import UserStatus as US

router = Router(name="commands")


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
    payload = _extract_start_payload(message)
    log_info(
        "user.start.requested",
        user_id=message.chat.id,
        status=status.value,
        authenticated=authenticated,
        payload_present=bool(payload),
    )
    try:
        if authenticated:
            manager = extend_dialog(dialog_manager)
            await dialog_manager.start(RootStates.start, mode=StartMode.RESET_STACK, show_mode=ShowMode.DELETE_AND_SEND)
            log_info("user.start.routed", user_id=message.chat.id, target_state=str(RootStates.start))
            if payload and payload != "default":
                if payload.startswith("meeting_"):
                    meeting_id_text = payload.removeprefix("meeting_")
                    if not meeting_id_text.isdigit():
                        log_warning(
                            "user.start.payload_invalid", user_id=message.chat.id, reason="meeting_id_not_digit"
                        )
                    else:
                        try:
                            meeting = await meeting_repo.get(int(meeting_id_text))
                        except LookupError:
                            log_warning(
                                "user.start.payload_invalid", user_id=message.chat.id, reason="meeting_not_found"
                            )
                        else:
                            await manager.state.set_meeting(meeting)
                            target_state = (
                                MeetingStates.info if status in (US.tutor, US.admin) else StudentMeetingStates.info
                            )
                            log_info("user.start.routed", user_id=message.chat.id, target_state=str(target_state))
                            return await manager.start(target_state, show_mode=ShowMode.DELETE_AND_SEND)
                if payload == "promoted_tutor":
                    if await tutor_repo.exists(telegram_id=message.chat.id):
                        self_tutor = await tutor_repo.get(telegram_id=message.chat.id)
                        await manager.state.set_self_tutor(self_tutor)
                        log_info(
                            "user.start.routed",
                            user_id=message.chat.id,
                            target_state=str(TutorProfileStates.profile_control),
                        )
                        return await manager.start(
                            TutorProfileStates.profile_control, show_mode=ShowMode.DELETE_AND_SEND
                        )
                    log_warning("user.start.payload_invalid", user_id=message.chat.id, reason="tutor_not_found")
                if payload == "settings":
                    log_info("user.start.routed", user_id=message.chat.id, target_state=str(RootStates.settings))
                    return await manager.start(RootStates.settings, show_mode=ShowMode.DELETE_AND_SEND)
                if payload == "guide":
                    log_info("user.start.routed", user_id=message.chat.id, target_state=str(GuideStates.notifications))
                    return await manager.start(GuideStates.notifications, show_mode=ShowMode.DELETE_AND_SEND)
            else:
                student = await manager.state.get_self_student()
                if not student.saw_guide:
                    log_info("user.start.routed", user_id=message.chat.id, target_state=str(GuideStates.init))
                    return await manager.start(GuideStates.init, show_mode=ShowMode.DELETE_AND_SEND)
        else:
            log_info("user.start.routed", user_id=message.chat.id, target_state=str(AuthStates.bind_tg_inh))
            return await dialog_manager.start(
                AuthStates.bind_tg_inh, mode=StartMode.RESET_STACK, show_mode=ShowMode.DELETE_AND_SEND
            )
    except Exception:
        log_error("user.start.failed", user_id=message.chat.id)
        raise


@router.message(~USER_AUTHENTICATED_FILTER, EMAIL_ENTERED_FILTER)
async def on_email(message: types.Message, state: FSMContext):
    # NOTE: needed just for MockAutoAuthMiddleware to work
    pass


# @router.message(Command("admin"), StatusFilter(US.admin))
# async def enable_admin_mode(message: types.Message, bot: Bot, dialog_manager: DialogManager):
#     text = "You are the Admin!"
#     await message.answer(text)
#     await bot.set_my_commands(
#         settings.bot_commands
#         or []
#         + [
#             types.BotCommand(command="admin", description="Enable admin mode"),
#         ],
#         scope=BotCommandScopeChat(chat_id=message.chat.id),
#     )
#     await dialog_manager.start(AdminStates.start, mode=StartMode.RESET_STACK)


# @router.message(Command("admin"), ~StatusFilter(US.admin))
# async def failed_enable_admin_mode(message: types.Message, bot: Bot):
#     text = "You are not the Admin!"
#     await message.answer(text)
#     await bot.set_my_commands(
#         settings.bot_commands or [],
#         scope=BotCommandScopeChat(chat_id=message.chat.id),
#     )


@router.message(Command("testapi"), StatusFilter(US.admin))
async def test_accounts_api(message: types.Message, dialog_manager: DialogManager):
    inh_user = await inh_accounts.get_user(telegram_id=message.chat.id)
    if inh_user is None:
        await message.answer("You're not found :(")
    else:
        await message.answer(f"Your inh id: {inh_user.id}")
