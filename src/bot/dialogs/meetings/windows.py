from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Cancel, Row, Start, SwitchTo
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
    Row(
        Cancel(Const("Back")),
        Button(Const("Create New"), id="create_meeting", on_click=open_meeting_create, when="is_admin"),
        Button(Const(" "), id="blank", on_click=None, when="is_tutor"),
    ),
    Button(Const("See Created"), id="a_meetings_created", on_click=omlot("created")),
    Button(Const("See Announced"), id="a_meetings_announced", on_click=omlot("announced")),
    Button(Const("See Closed"), id="a_meetings_closed", on_click=omlot("closed")),
    state=MeetingStates.type,
    getter=user_status_getter,
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
    Format("Title: {title}"),
    Format("Status: {status.name}\n"),
    Format("Date: {date}"),
    Format("Duration: {duration}"),
    Format("Tutor: @{tutor_username}"),
    Format("Description: {description}", when="description"),
    Start(text=Const("Change Info"), id="change_init", state=ChangeStates.init, show_mode=ShowMode.EDIT),
    Button(Const("Announce"), id="announce_start", on_click=open_announce_confirm, when="can_be_announced"),
    Button(Const("Delete"), id="delete_start", on_click=open_delete_confirm, when="can_be_deleted"),
    Row(SwitchTo(Const("Back"), "to_list", MeetingStates.list), BLANK_BUTTON),
    state=MeetingStates.info,
    getter=meeting_info_getter,
)


announce_confirm_ww = Window(
    Format('Are you surely ready to announce "{title}"?'),
    Row(
        Button(Const("Announce 📣"), id="announce", when="can_be_announced", on_click=on_announce_confirmed),
        SwitchTo(Const("Cancel"), id="cancel_announce", state=MeetingStates.info),
    ),
    state=MeetingStates.announce_confirm,
    getter=meeting_info_getter,
)


delete_confirm_ww = Window(
    Format('Do you really want to delete "{title}"?'),
    Row(
        Button(Const("Delete 🗑️"), id="delete", when="can_be_deleted", on_click=on_delete_confirmed),
        SwitchTo(Const("Cancel"), id="cancel_delete", state=MeetingStates.info),
    ),
    state=MeetingStates.delete_confirm,
    getter=meeting_info_getter,
)
