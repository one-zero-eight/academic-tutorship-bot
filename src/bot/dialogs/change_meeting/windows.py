from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Calendar, Cancel, Column, Row, SwitchTo

from src.bot.custom_widgets import MeetingInfoText
from src.bot.filters import *
from src.bot.i18n import I18NFormat as I18N

from .dialog_buttons import *
from .getters import *
from .handles import *
from .states import *

info_change_ww = Window(
    MeetingInfoText(admin_info=True),
    Column(
        SwitchTo(I18N("CHANGE_INFO_BTN_SET_TITLE"), id="change_title", state=ChangeStates.title),
        SwitchTo(I18N("CHANGE_INFO_BTN_SET_DESCRIPTION"), id="set_description", state=ChangeStates.description),
        SwitchTo(I18N("CHANGE_INFO_BTN_SET_ROOM"), id="set_room", state=ChangeStates.room),
        SwitchTo(I18N("CHANGE_INFO_BTN_SET_DATE"), id="choose_date", state=ChangeStates.date),
        SwitchTo(I18N("CHANGE_INFO_BTN_SET_DURATION"), id="choose_duration", state=ChangeStates.duration),
        SwitchTo(
            I18N("CHANGE_INFO_BTN_ASSIGN_TUTOR"),
            id="assign_tutor",
            state=ChangeStates.tutor,
            on_click=open_assign_tutor,
            when="is_admin",
        ),
    ),
    Row(Cancel(I18N("COMMON_BTN_BACK")), BTN_BLANK),
    state=ChangeStates.init,
    getter=meeting_info_getter,
)


set_title_ww = Window(
    I18N("CHANGE_SET_TITLE_PROMPT"),
    Row(BTN_INIT, BTN_BLANK),
    MessageInput(get_meeting_title),
    state=ChangeStates.title,
    getter=meeting_info_getter,
)


set_description_ww = Window(
    I18N("CHANGE_SET_DESCRIPTION_PROMPT"),
    Row(BTN_INIT, BTN_BLANK),
    MessageInput(get_meeting_description),
    state=ChangeStates.description,
    getter=meeting_info_getter,
)


set_room_ww = Window(
    I18N("CHANGE_SET_ROOM_PROMPT"),
    Row(BTN_INIT, BTN_BLANK),
    MessageInput(get_meeting_room),
    state=ChangeStates.room,
    getter=meeting_info_getter,
)


set_date_ww = Window(
    I18N("CHANGE_SET_DATE_PROMPT"),
    Calendar(id="set_date_calendar", on_click=on_date_selected),  # type: ignore
    Row(BTN_INIT, BTN_BLANK),
    state=ChangeStates.date,
    getter=meeting_info_getter,
)


set_time_ww = Window(
    I18N("CHANGE_SET_TIME_PROMPT"),
    MessageInput(get_meeting_time),
    Row(
        SwitchTo(text=I18N("COMMON_BTN_BACK"), id="to_date", state=ChangeStates.date, on_click=handle_clear),
        BTN_BLANK,
    ),
    state=ChangeStates.time,
    getter=meeting_info_getter,
)


set_duration_ww = Window(
    I18N("CHANGE_SET_DURATION_PROMPT"),
    Row(BTN_INIT, BTN_BLANK),
    MessageInput(get_meeting_duration),
    state=ChangeStates.duration,
    getter=meeting_info_getter,
)


assign_tutor_ww = Window(
    I18N("CHANGE_ASSIGN_TUTOR_TITLE"),
    TUTORS_ASSIGN_SCROLLING_GROUP,
    Row(BTN_INIT, BTN_BLANK),
    MessageInput(get_assigned_tutor),
    state=ChangeStates.tutor,
    getter=meeting_info_with_tutors_getter,
)
