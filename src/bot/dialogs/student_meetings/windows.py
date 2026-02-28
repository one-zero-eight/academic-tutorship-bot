from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Cancel, Row, SwitchTo
from aiogram_dialog.widgets.text import Const, Format

from src.bot.dto import *
from src.bot.filters import *

from .dialog_buttons import *
from .getters import *
from .states import *

list_ww: Window = Window(
    Format("Upcoming Meetings"),
    MEETINGS_SCROLLING_GROUP,
    Row(Cancel(Const("Back"), "cancel"), BLANK_BUTTON),
    state=StudentMeetingStates.list,
    getter=meetings_list_getter,
)


info_ww = Window(
    Const("Meeting Info"),
    Format("Title: {title}"),
    Format("Status: {status.name}"),
    Format("Attendance: {attendance_count}", when="attendance_count"),
    Const(" "),
    Format("Date: {date}"),
    Format("Duration: {duration}"),
    Format("Tutor: @{tutor_username}"),
    Format("Description: {description}", when="description"),
    Row(SwitchTo(Const("Back"), "to_list", StudentMeetingStates.list), BLANK_BUTTON),
    state=StudentMeetingStates.info,
    getter=meeting_info_getter,
)
