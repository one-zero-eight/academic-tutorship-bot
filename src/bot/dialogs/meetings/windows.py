from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Cancel, Row, SwitchTo
from aiogram_dialog.widgets.text import Const, Format

from src.bot.dialogs.change_meeting import ChangeStates
from src.bot.dto import *
from src.bot.filters import *

from .dialog_buttons import *
from .getters import *
from .handles import *
from .states import *

omlot = open_meetings_list_of_type

type_ww: Window = Window(
    Const("Meetings"),
    Row(Cancel(), Button(Const("Create New"), id="a_create_meeting", on_click=open_meeting_create)),
    Button(Const("See Created"), id="a_meetings_created", on_click=omlot("created")),
    Button(Const("See Announced"), id="a_meetings_announced", on_click=omlot("announced")),
    Button(Const("See Closed"), id="a_meetings_closed", on_click=omlot("closed")),
    state=MeetingStates.type,
)

del omlot


list_ww: Window = Window(
    Format("{meetings_type} Meetings"),
    MEETINGS_SCROLLING_GROUP,
    Row(SwitchTo(Const("Back"), "to_type", MeetingStates.type), BLANK_BUTTON),
    state=MeetingStates.list,
    getter=meetings_list_getter,
)


create_ww = Window(
    Const("Create New Meeting"),
    Const("Enter Title:"),
    MessageInput(get_new_title),
    Row(SwitchTo(Const("Back"), "to_type", MeetingStates.type), BLANK_BUTTON),
    state=MeetingStates.create,
)


info_ww = Window(
    Const("Meeting Info"),
    Format("{title}"),
    Format("Date: {date}"),
    Format("Duration: {duration}"),
    Format("Tutor: @{tutor_username}"),
    Format("{description}", when="description"),
    StartWithData(text=Const("Change Info"), id="change_init", state=ChangeStates.init, show_mode=ShowMode.EDIT),
    Row(SwitchTo(Const("Back"), "to_list", MeetingStates.list), BLANK_BUTTON),
    state=MeetingStates.info,
    getter=meeting_info_getter,
)
