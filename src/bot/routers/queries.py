from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InaccessibleMessage
from aiogram_dialog import DialogManager, ShowMode

from src.bot.dialogs.attendance import AttendanceStates
from src.bot.dto import *
from src.db.repositories import meetings_repo

router = Router(name="queries")


@router.callback_query(F.data == "delete_warning")
async def on_delete_warning(query: CallbackQuery, dialog_manager: DialogManager):
    if not query.message:
        raise ValueError("No query.message")
    if isinstance(query.message, InaccessibleMessage):
        raise ValueError("query.message is InaccessibleMessage")
    await query.message.delete()


@router.callback_query(F.data.startswith("open-send-attendance"))
async def on_open_send_attendance_from_notification(
    query: CallbackQuery, dialog_manager: DialogManager, state: FSMContext
):
    if not query.message:
        raise ValueError("No query.message")
    if isinstance(query.message, InaccessibleMessage):
        raise ValueError("query.message is InaccessibleMessage")

    try:
        meeting_id = int(str(query.data).split("_")[1])
        meeting = await meetings_repo.get(id=meeting_id)
    except Exception as e:
        return await query.answer(f"Error: {e}", show_alert=True)

    if meeting.attendance is not None:
        await query.answer("Attendance already assigned", show_alert=True)
        await query.message.edit_reply_markup(reply_markup=None)
        return

    await state.update_data({"meeting": meeting_to_dto(meeting)})
    await dialog_manager.start(AttendanceStates.close, show_mode=ShowMode.DELETE_AND_SEND)

    # TODO: finish this
    #       - check is admin or tutor
    #       - come up with how to collect file
    #
    #       - maybe set meeting and meetings_list in state.data
    #         and switch to ChangeStates.attendance step-by-step? (to keep stack as needed)
    #           - Admin/TutorStates.start  (new stack)
    #           - start MeetingStates.init
    #           - start ChangeStates.change
    #
    #       - maybe create separate AttendanceDialog for one-time use?
    ...
