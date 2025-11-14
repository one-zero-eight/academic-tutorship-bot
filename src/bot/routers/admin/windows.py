from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Back, Button, Row, ScrollingGroup
from aiogram_dialog.widgets.text import Const, Format

from src.bot.filters import *
from src.domain.models import *

from .dialog_buttons import *
from .getters import *
from .handles import *
from .states import *

admin_menu_ww: Window = Window(
    Const("Admin Panel"),
    Button(Const("Meetings"), id="a_meetings", on_click=open_meetings_type_choice),
    state=AdminStates.menu,
)


omlot = open_meetings_list_of_type

admin_meetings_type_ww: Window = Window(
    Const("Meetings"),
    Row(Back(), Button(Const("Create New"), id="a_create_meeting", on_click=open_meeting_create)),
    Button(Const("See Created"), id="a_meetings_created", on_click=omlot("created")),
    Button(Const("See Announced"), id="a_meetings_announced", on_click=omlot("announced")),
    Button(Const("See Closed"), id="a_meetings_closed", on_click=omlot("closed")),
    state=AdminStates.meetings_type,
)

del omlot


admin_meetings_list_ww: Window = Window(
    Format("{meetings_type} Meetings"),
    BTN_ROW_BACK,
    ScrollingGroup(
        *meeting_buttons(TEST_MEETINGS),
        id="a_meetings_list",
        width=1,
        height=3,
    ),
    state=AdminStates.meetings_list,
    getter=meetings_list_getter,
)


admin_create_meeting_ww = Window(
    Const("Create New Meeting"),
    Const("Enter Title:"),
    MessageInput(get_title_of_meeting),
    Row(Button(Const("Back"), id="create_back", on_click=open_meetings_type_choice), BLANK_BUTTON),
    state=AdminStates.create_meeting,
)


admin_meeting_info_ww = Window(
    Const("Meeting Info"),
    Format("{title}"),
    Format("Date: {date}"),
    Format("Duration: {duration}"),
    Format("Tutor: {tutor_username}"),
    Format("{description}", when="description"),
    Row(Button(Const("Back"), id="back_window_info", on_click=open_meetings_type_choice), BLANK_BUTTON),
    Button(Const("Assign Tutor"), id="assign_tutor", on_click=open_assign_tutor),
    state=AdminStates.meeting_info,
    getter=meeting_info_getter,
)


admin_assign_tutor_ww = Window(
    Format('Assign Tutor to "{title}"'),
    Row(Button(Const("Back"), id="back_assign_tutor", on_click=open_meeting_info), BLANK_BUTTON),
    MessageInput(get_assigned_tutor),
    state=AdminStates.assign_tutor,
    getter=meeting_info_getter,
)


admin_confirm_tutor_ww = Window(
    Format('Assign Tutor @{tutor} to "{title}"'),
    Row(
        Button(Const("Confirm"), id="confirm_tutor", on_click=confirm_tutor_open_meeting_info),
        Button(Const("ReChoose"), id="rechoose_tutor", on_click=open_assign_tutor),
    ),
    state=AdminStates.confirm_tutor,
    getter=meeting_info_getter,
)
