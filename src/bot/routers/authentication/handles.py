from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button

from src.bot.filters import UserStatus
from src.bot.routers.admin import AdminStates
from src.bot.routers.student import StudentStates

# from src.bot.routers.tutor import TutorStates


async def check_connected(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    # NOTE: data required from AutoAuthMiddleware
    authenticated = dialog_manager.middleware_data["authenticated"]
    status = dialog_manager.middleware_data["status"]

    if not authenticated:
        await query.answer("You are not authenticated yet, try again")
        return

    match status:
        case UserStatus.admin:
            target_state = AdminStates.start
        case UserStatus.student:
            target_state = StudentStates.start
        # case UserStatus.tutor:
        #     target_state = TutorStates.start

    await query.answer("Authentication Success ✅")
    await dialog_manager.start(state=target_state, mode=StartMode.RESET_STACK)
