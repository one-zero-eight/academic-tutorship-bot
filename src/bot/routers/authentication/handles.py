from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button

from src.bot.filters import UserStatus
from src.bot.logging_ import log_info, log_warning
from src.bot.routers.admin import AdminStates
from src.bot.routers.student import StudentStates
from src.bot.routers.tutor import TutorStates


async def check_connected(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    log_info("auth.check_connected.requested", user_id=query.from_user.id)
    # NOTE: data required from AutoAuthMiddleware
    authenticated = dialog_manager.middleware_data["authenticated"]
    status = dialog_manager.middleware_data["status"]

    if not authenticated:
        log_warning("auth.check_connected.unauthenticated", user_id=query.from_user.id)
        return await query.answer("You are not authenticated yet, try again")

    match status:
        case UserStatus.admin:
            target_state = AdminStates.start  # noqa E701
        case UserStatus.tutor:
            target_state = TutorStates.start  # noqa E701
        case UserStatus.student:
            target_state = StudentStates.start  # noqa E701

    await query.answer("Authentication Success ✅")
    log_info(
        "auth.check_connected.succeeded",
        user_id=query.from_user.id,
        status=status.value,
        target_state=str(target_state),
    )
    await dialog_manager.start(state=target_state, mode=StartMode.RESET_STACK)
