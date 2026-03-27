from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Cancel, Row, SwitchTo

from src.bot.custom_widgets import MeetingInfoText
from src.bot.dialogs.meetings.getters import meeting_info_getter
from src.bot.filters import *
from src.bot.i18n import I18NFormat as I18N
from src.bot.utils import BLANK_BTN

from .getters import *
from .handles import *
from .states import *

init_ww = Window(
    MeetingInfoText(admin_info=True),
    SwitchTo(text=I18N("ATTENDANCE_BTN_RESEND_FILE"), state=AttendanceStates.resend, id="to_update"),
    SwitchTo(text=I18N("ATTENDANCE_BTN_ADD_EMAIL"), state=AttendanceStates.add_email, id="to_add_email"),
    Button(text=I18N("ATTENDANCE_BTN_DOWNLOAD_FILE"), id="download_attendance", on_click=on_download_attendance),
    Row(Cancel(I18N("COMMON_BTN_BACK")), BLANK_BTN),
    getter=meeting_info_getter,
    state=AttendanceStates.init,
)

resend_ww = Window(
    I18N("ATTENDANCE_RESEND_TITLE"),
    Row(
        SwitchTo(I18N("COMMON_BTN_BACK"), state=AttendanceStates.init, id="to_attendance_init", on_click=handle_clear),
        BLANK_BTN,
    ),
    MessageInput(get_attendance_file_resend),
    getter=meeting_info_getter,
    state=AttendanceStates.resend,
)

close_ww = Window(
    I18N("ATTENDANCE_CLOSE_TITLE"),
    Row(Cancel(I18N("COMMON_BTN_BACK"), on_click=handle_clear), BLANK_BTN),
    MessageInput(get_attendance_file_close),
    getter=meeting_info_getter,
    state=AttendanceStates.close,
)

add_email_ww = Window(
    I18N("ATTENDANCE_ADD_EMAIL_PROMPT"),
    Row(
        SwitchTo(I18N("COMMON_BTN_BACK"), state=AttendanceStates.init, id="to_attendance_init", on_click=handle_clear),
        BLANK_BTN,
    ),
    MessageInput(get_email_to_add),
    getter=meeting_info_getter,
    state=AttendanceStates.add_email,
)
