from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Calendar, Cancel, Column, Row, SwitchTo
from aiogram_dialog.widgets.text import Const, Format

from src.bot.custom_widgets import MeetingInfoText
from src.bot.filters import *
from src.bot.utils import COMMON_BACK_TEXT

from .dialog_buttons import *
from .getters import *
from .handles import *
from .states import *

info_change_ww = Window(
    MeetingInfoText(admin_info=True),
    Column(
        SwitchTo(Const("Set Title"), id="change_title", state=ChangeStates.title),
        SwitchTo(Const("Set Description"), id="set_description", state=ChangeStates.description),
        SwitchTo(Const("Set Room"), id="set_room", state=ChangeStates.room),
        SwitchTo(Const("Set Date"), id="choose_date", state=ChangeStates.date),
        SwitchTo(Const("Set Duration"), id="choose_duration", state=ChangeStates.duration),
        SwitchTo(
            Const("Assign Tutor"),
            id="assign_tutor",
            state=ChangeStates.tutor,
            on_click=open_assign_tutor,
            when="is_admin",
        ),
    ),
    Row(Cancel(COMMON_BACK_TEXT), BTN_BLANK),
    state=ChangeStates.init,
    getter=meeting_info_getter,
)


set_title_ww = Window(
    Format('Enter new Title for "{title}"'),
    Row(BTN_INIT, BTN_BLANK),
    MessageInput(get_meeting_title),
    state=ChangeStates.title,
    getter=meeting_info_getter,
)


set_description_ww = Window(
    Format('Enter new Description for "{title}"'),
    Row(BTN_INIT, BTN_BLANK),
    MessageInput(get_meeting_description),
    state=ChangeStates.description,
    getter=meeting_info_getter,
)


set_room_ww = Window(
    Format('Enter new Room for "{title}"'),
    Row(BTN_INIT, BTN_BLANK),
    MessageInput(get_meeting_room),
    state=ChangeStates.room,
    getter=meeting_info_getter,
)


set_date_ww = Window(
    Format('Enter new Date for "{title}"'),
    Calendar(id="set_date_calendar", on_click=on_date_selected),  # type: ignore
    Row(BTN_INIT, BTN_BLANK),
    state=ChangeStates.date,
    getter=meeting_info_getter,
)


set_time_ww = Window(
    Format('Enter new Time for "{title}"'),
    Const("Adhere to format 00:00, e.g. 20:32"),
    MessageInput(get_meeting_time),
    Row(
        SwitchTo(text=COMMON_BACK_TEXT, id="to_date", state=ChangeStates.date, on_click=handle_clear),
        BTN_BLANK,
    ),
    state=ChangeStates.time,
    getter=meeting_info_getter,
)


set_duration_ww = Window(
    Format('Enter new Duration for "{title}"'),
    Const('In format "hh:mm"'),
    Row(BTN_INIT, BTN_BLANK),
    MessageInput(get_meeting_duration),
    state=ChangeStates.duration,
    getter=meeting_info_getter,
)


assign_tutor_ww = Window(
    Format('Assign Tutor to "{title}"\n'),
    Const("Here's the list of all tutors for reference"),
    TUTORS_ASSIGN_SCROLLING_GROUP,
    Row(BTN_INIT, BTN_BLANK),
    MessageInput(get_assigned_tutor),
    state=ChangeStates.tutor,
    getter=meeting_info_with_tutors_getter,
)
