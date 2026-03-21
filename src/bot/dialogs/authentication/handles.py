from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button

from src.bot.dialogs.root import RootStates
from src.bot.logging_ import log_info, log_warning


async def check_connected(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    log_info("auth.check_connected.requested", user_id=query.from_user.id)
    # NOTE: data required from AutoAuthMiddleware
    authenticated = dialog_manager.middleware_data["authenticated"]
    status = dialog_manager.middleware_data["status"]

    if not authenticated:
        log_warning("auth.check_connected.unauthenticated", user_id=query.from_user.id)
        return await query.answer("You are not authenticated yet, try again")

    await query.answer("Authentication Success ✅")
    log_info(
        "auth.check_connected.succeeded",
        user_id=query.from_user.id,
        status=status.value,
    )
    await dialog_manager.start(state=RootStates.start, mode=StartMode.RESET_STACK)
