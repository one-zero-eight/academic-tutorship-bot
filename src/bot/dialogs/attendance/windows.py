from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Cancel, Row, SwitchTo
from aiogram_dialog.widgets.text import Const, Format

from src.bot.custom_widgets import MeetingInfoText
from src.bot.dialogs.meetings.getters import meeting_info_getter
from src.bot.filters import *
from src.bot.utils import BLANK_BTN, COMMON_BACK_TEXT

from .getters import *
from .handles import *
from .states import *

init_ww = Window(
    MeetingInfoText(admin_info=True),
    SwitchTo(text=Const("Resend File"), state=AttendanceStates.resend, id="to_update"),
    SwitchTo(text=Const("Add email"), state=AttendanceStates.add_email, id="to_add_email"),
    Button(text=Const("Download File"), id="download_attendance", on_click=on_download_attendance),
    Row(Cancel(COMMON_BACK_TEXT), BLANK_BTN),
    getter=meeting_info_getter,
    state=AttendanceStates.init,
)

resend_ww = Window(
    Format('Resend attendance file for "{title}"'),
    Row(
        SwitchTo(COMMON_BACK_TEXT, state=AttendanceStates.init, id="to_attendance_init", on_click=handle_clear),
        BLANK_BTN,
    ),
    MessageInput(get_attendance_file_resend),
    getter=meeting_info_getter,
    state=AttendanceStates.resend,
)

close_ww = Window(
    Format('Send attendance file to close "{title}"'),
    Row(Cancel(COMMON_BACK_TEXT, on_click=handle_clear), BLANK_BTN),
    MessageInput(get_attendance_file_close),
    getter=meeting_info_getter,
    state=AttendanceStates.close,
)

add_email_ww = Window(
    Format("Enter email of a person to add 👤"),
    Row(
        SwitchTo(COMMON_BACK_TEXT, state=AttendanceStates.init, id="to_attendance_init", on_click=handle_clear),
        BLANK_BTN,
    ),
    MessageInput(get_email_to_add),
    getter=meeting_info_getter,
    state=AttendanceStates.add_email,
)
