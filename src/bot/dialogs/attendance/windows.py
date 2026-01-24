from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Cancel, Row, SwitchTo
from aiogram_dialog.widgets.text import Const, Format

from src.bot.dialogs.meetings.getters import meeting_info_getter
from src.bot.dto import *
from src.bot.filters import *

from .getters import *
from .handles import *
from .states import *

init_ww = Window(
    Const("Meeting Info"),
    Format("Title: {title}"),
    Format("Status: {status.name}"),
    Format("Attendance: {attendance_count}", when="attendance_count"),
    Const(" "),
    Format("Date: {date}"),
    Format("Duration: {duration}"),
    Format("Tutor: @{tutor_username}"),
    Format("Description: {description}", when="description"),
    SwitchTo(text=Const("Resend File"), state=AttendanceStates.resend, id="to_update"),
    SwitchTo(text=Const("Add email"), state=AttendanceStates.add_email, id="to_add_email"),
    Button(text=Const("Download File"), id="download_attendance", on_click=on_download_attendance),
    Row(Cancel(Const("Back")), Button(Const(" "), id="blank", on_click=None)),
    getter=meeting_info_getter,
    state=AttendanceStates.init,
)

resend_ww = Window(
    Format('Resend attendance file for "{title}"'),
    Row(
        SwitchTo(Const("Back"), state=AttendanceStates.init, id="to_attendance_init"),
        Button(Const(" "), id="blank", on_click=None),
    ),
    MessageInput(get_attendance_file_resend),
    getter=meeting_info_getter,
    state=AttendanceStates.resend,
)

close_ww = Window(
    Format('Send attendance file to close "{title}"'),
    Row(Cancel(Const("Back")), Button(Const(" "), id="blank", on_click=None)),
    MessageInput(get_attendance_file_close),
    getter=meeting_info_getter,
    state=AttendanceStates.close,
)

add_email_ww = Window(
    Format("Enter email of a person to add 👤"),
    Row(
        SwitchTo(Const("Back"), state=AttendanceStates.init, id="to_attendance_init"),
        Button(Const(" "), id="blank", on_click=None),
    ),
    MessageInput(get_email_to_add),
    getter=meeting_info_getter,
    state=AttendanceStates.add_email,
)
