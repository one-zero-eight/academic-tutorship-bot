from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Back, Button, Column, Row, SwitchTo
from aiogram_dialog.widgets.text import Const, Format

from src.bot.filters import *
from src.domain.models import *

from .dialog_buttons import *
from .getters import *
from .handles import *
from .states import *

admin_start_ww: Window = Window(
    Const("Admin Panel"),
    Button(Const("Meetings"), id="a_meetings", on_click=open_meetings_type_choice),
    SwitchTo(Const("Tutors"), id="a_tutors", state=AdminStates.tutors_list),
    state=AdminStates.start,
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
    MEETINGS_SCROLLING_GROUP,
    BTN_ROW_BACK,
    state=AdminStates.meetings_list,
    getter=meetings_list_getter,
)


admin_create_meeting_ww = Window(
    Const("Create New Meeting"),
    Const("Enter Title:"),
    MessageInput(get_new_title),
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
    SwitchTo(Const("Change Info"), id="change_meeting", state=AdminStates.meeting_change),
    Row(Button(Const("Back"), id="back_window_info", on_click=open_meetings_type_choice), BLANK_BUTTON),
    state=AdminStates.meeting_info,
    getter=meeting_info_getter,
)


admin_meeting_change_ww = Window(
    Const("Meeting Info"),
    Format("{title}"),
    Format("Date: {date}"),
    Format("Duration: {duration}"),
    Format("Tutor: {tutor_username}"),
    Format("{description}", when="description"),
    Column(
        Button(Const("Set Title"), id="change_title", on_click=open_set_title),
        Button(Const("Set Description"), id="set_description", on_click=open_set_description),
        Button(Const("Set Date"), id="choose_date", on_click=open_set_date),
        Button(Const("Set Duration"), id="choose_duration", on_click=open_set_duration),
        Button(Const("Assign Tutor"), id="assign_tutor", on_click=open_assign_tutor),
    ),
    Row(SwitchTo(Const("Back"), id="back_window_change", state=AdminStates.meeting_info), BLANK_BUTTON),
    state=AdminStates.meeting_change,
    getter=meeting_info_getter,
)


admin_assign_tutor_ww = Window(
    Format('Assign Tutor to "{title}"'),
    Row(Button(Const("Back"), id="back_assign_tutor", on_click=open_meeting_info), BLANK_BUTTON),
    MessageInput(get_assigned_tutor),
    state=AdminStates.assign_tutor,
    getter=meeting_info_getter,
)


admin_set_title_ww = Window(
    Format('Enter new Title for "{title}"'),
    Row(SwitchTo(Const("Back"), id="st1", state=AdminStates.meeting_change), BLANK_BUTTON),
    MessageInput(get_meeting_title),
    state=AdminStates.set_title,
    getter=meeting_info_getter,
)


admin_set_description_ww = Window(
    Format('Enter new Description for "{title}"'),
    Row(SwitchTo(Const("Back"), id="st1", state=AdminStates.meeting_change), BLANK_BUTTON),
    MessageInput(get_meeting_description),
    state=AdminStates.set_description,
    getter=meeting_info_getter,
)


admin_set_date_ww = Window(
    Format('Enter new Date for "{title}"'),
    Const('In format "DD.MM.YYYY"'),
    Row(SwitchTo(Const("Back"), id="st1", state=AdminStates.meeting_change), BLANK_BUTTON),
    MessageInput(get_meeting_date),
    state=AdminStates.set_date,
    getter=meeting_info_getter,
)


admin_set_duration_ww = Window(
    Format('Enter new Duration for "{title}"'),
    Const('In format "hh:mm"'),
    Row(SwitchTo(Const("Back"), id="st1", state=AdminStates.meeting_change), BLANK_BUTTON),
    MessageInput(get_meeting_duration),
    state=AdminStates.set_duration,
    getter=meeting_info_getter,
)


admin_tutors_list_ww = Window(
    Const("Tutors List"),
    TUTORS_SCROLLING_GROUP,
    Row(
        HOME_BUTTON,
        Button(Const("Add New"), id="add_tutor", on_click=open_add_tutor),
    ),
    state=AdminStates.tutors_list,
    getter=tutors_list_getter,
)


admin_tutor_info_ww = Window(
    Format("Tutor [{id}] Info"),
    Format("{full_name}"),
    Format("@{username}"),
    Format("telegram id: <code>{tg_id}</code>"),
    Button(Const("Dismiss"), id="rm_tutor", on_click=on_remove_tutor),
    Row(SwitchTo(Const("Back"), id="back_window_change", state=AdminStates.tutors_list), BLANK_BUTTON),
    state=AdminStates.tutor_info,
    getter=tutor_info_getter,
    parse_mode="HTML",
)


admin_add_tutor_ww = Window(
    Const("Share contact of the new Tutor"),
    Row(Button(Const("Back"), id="back_add_tutor", on_click=open_tutors_list_with_clear), BLANK_BUTTON),
    MessageInput(get_added_tutor),
    state=AdminStates.add_tutor,
)
