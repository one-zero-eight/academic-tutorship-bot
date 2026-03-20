from aiogram import F, Router
from aiogram.types import CallbackQuery, InaccessibleMessage
from aiogram_dialog import DialogManager

router = Router(name="queries")


@router.callback_query(F.data == "delete_warning")
async def on_delete_warning(query: CallbackQuery, dialog_manager: DialogManager):
    if not query.message:
        raise ValueError("No query.message")
    if isinstance(query.message, InaccessibleMessage):
        raise ValueError("query.message is InaccessibleMessage")
    await query.message.delete()
