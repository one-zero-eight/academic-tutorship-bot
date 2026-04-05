from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Cancel, Next, Row, Start, SwitchTo
from aiogram_dialog.widgets.text import Const

from src.bot.custom_widgets import MeetingInfoText
from src.bot.dialogs.attendance.states import AttendanceStates
from src.bot.dialogs.change_meeting.states import ChangeStates
from src.bot.dialogs.discipline_picker.states import DisciplinePickerStates
from src.bot.dialogs.tutors_profile.handles import open_tutor_profile
from src.bot.dialogs.tutors_profile.states import TutorProfileStates
from src.bot.filters import *
from src.bot.i18n import I18NFormat as I18N

from .dialog_buttons import *
from .getters import *
from .handles import *
from .states import *

omlot = open_meetings_list_of_type

type_ww: Window = Window(
    I18N("MEETINGS_TYPE_TITLE"),
    Button(
        I18N("MEETINGS_BTN_SEE_CREATED"), id="a_meetings_created", on_click=omlot("created"), when="can_see_created"
    ),
    Button(
        I18N("MEETINGS_BTN_SEE_APPROVING"),
        id="a_meetings_approving",
        on_click=omlot("approving"),
        when="can_see_approving",
    ),
    Button(
        I18N("MEETINGS_BTN_SEE_ANNOUNCED"),
        id="a_meetings_announced",
        on_click=omlot("announced"),
        when="can_see_announced",
    ),
    Button(I18N("MEETINGS_BTN_SEE_CLOSED"), id="a_meetings_closed", on_click=omlot("closed"), when="can_see_closed"),
    Row(
        Cancel(I18N("COMMON_BTN_BACK")),
        SwitchTo(I18N("MEETINGS_BTN_CREATE_NEW"), id="create_meeting", state=MeetingStates.create),
    ),
    state=MeetingStates.type,
    getter=meetings_type_getter,
)

del omlot


list_ww: Window = Window(
    I18N("MEETINGS_LIST_CREATED_TITLE", when="type_created"),
    I18N("MEETINGS_LIST_APPROVING_TITLE", when="type_approving"),
    I18N("MEETINGS_LIST_ANNOUNCED_TITLE", when="type_announced"),
    I18N("MEETINGS_LIST_CLOSED_TITLE", when="type_closed"),
    MEETINGS_SCROLLING_GROUP,
    Row(SwitchTo(I18N("COMMON_BTN_BACK"), "to_type", MeetingStates.type), BLANK_BUTTON),
    state=MeetingStates.list,
    getter=meetings_list_getter,
)

create_ww = Window(
    I18N("MEETING_CREATE_TITLE"),
    Row(
        Next(I18N("MEETING_CREATE_BTN_TITLE")),
        Start(I18N("MEETING_CREATE_BTN_DISCIPLINE"), id="choose_discipline", state=DisciplinePickerStates.language),
    ),
    Row(
        SwitchTo(I18N("COMMON_BTN_BACK"), "to_type", MeetingStates.type),
        Button(Const(" "), id="blank", when="cannot_be_created"),
        Button(I18N("MEETING_CREATE_BTN_SUBMIT"), id="create_submit", on_click=on_create_submit, when="can_be_created"),
    ),
    getter=meeting_create_getter,
    state=MeetingStates.create,
)

create_enter_title_ww = Window(
    I18N("MEETING_CREATE_ENTER_TITLE_TITLE"),
    MessageInput(get_new_title),
    Row(SwitchTo(I18N("COMMON_BTN_BACK"), "to_type", MeetingStates.type), BLANK_BUTTON),
    getter=meeting_create_getter,
    state=MeetingStates.create_title,
)


info_ww = Window(
    MeetingInfoText(admin_info=True),
    Start(
        text=I18N("MEETING_INFO_BTN_CHANGE_INFO"),
        id="change_init",
        state=ChangeStates.init,
        show_mode=ShowMode.EDIT,
        when="can_be_changed",
    ),
    Button(
        I18N("STUDENT_MEETING_BTN_TUTOR_PROFILE"),
        id="to_tutor_profile",
        when="can_see_tutor_profile",
        on_click=open_tutor_profile,
    ),
    Start(
        I18N("STUDENT_MEETING_BTN_TO_YOUR_PROFILE"),
        id="to_tutor_profile_control",
        state=TutorProfileStates.profile_control,
        when="can_see_tutor_profile_control",
    ),
    Button(
        I18N("MEETING_INFO_BTN_ANNOUNCE"), id="announce_start", on_click=open_announce_confirm, when="can_be_announced"
    ),
    Button(
        I18N("MEETING_INFO_BTN_SEND_FOR_APPROVAL"),
        id="approval_start",
        on_click=open_send_for_approval_confirm,
        when="can_be_sent_for_approval",
    ),
    Button(I18N("MEETING_INFO_BTN_FINISH"), id="finish_start", on_click=open_finish_confirm, when="can_be_finished"),
    Start(I18N("MEETING_INFO_BTN_CLOSE"), id="start_close", state=AttendanceStates.close, when="can_be_closed"),
    Start(
        I18N("MEETING_INFO_BTN_ATTENDANCE"),
        id="start_attendance",
        state=AttendanceStates.init,
        when="can_see_attendance",
    ),
    SwitchTo(
        I18N("MEETING_INFO_BTN_CANCEL_MEETING"),
        id="cancel_meeting_start",
        state=MeetingStates.delete_confirm,
        when="can_be_deleted",
    ),
    Row(SwitchTo(I18N("COMMON_BTN_BACK"), "to_list", MeetingStates.list), BLANK_BUTTON),
    state=MeetingStates.info,
    getter=meeting_info_getter,
)


send_for_approval_confirm_ww = Window(
    I18N("MEETING_CONFIRM_SEND_FOR_APPROVAL_TITLE"),
    Row(
        Button(
            I18N("MEETING_CONFIRM_SEND_FOR_APPROVAL_BTN"),
            id="send_for_approval",
            when="can_be_sent_for_approval",
            on_click=on_send_for_approval_confirmed,
        ),
        SwitchTo(I18N("COMMON_BTN_CANCEL"), id="cancel_send_for_approval", state=MeetingStates.info),
    ),
    state=MeetingStates.send_for_approval_confirm,
    getter=meeting_info_getter,
)


announce_confirm_ww = Window(
    I18N("MEETING_CONFIRM_ANNOUNCE_TITLE"),
    Row(
        Button(
            I18N("MEETING_CONFIRM_ANNOUNCE_BTN"), id="announce", when="can_be_announced", on_click=on_announce_confirmed
        ),
        SwitchTo(I18N("COMMON_BTN_CANCEL"), id="cancel_announce", state=MeetingStates.info),
    ),
    state=MeetingStates.announce_confirm,
    getter=meeting_info_getter,
)


finish_confirm_ww = Window(
    I18N("MEETING_CONFIRM_FINISH_TITLE"),
    Row(
        Button(I18N("MEETING_CONFIRM_FINISH_BTN"), id="finish", when="can_be_finished", on_click=on_finish_confirmed),
        SwitchTo(I18N("COMMON_BTN_CANCEL"), id="cancel_finish", state=MeetingStates.info),
    ),
    state=MeetingStates.finish_confirm,
    getter=meeting_info_getter,
)


delete_confirm_ww = Window(
    I18N("MEETING_CONFIRM_DELETE_TITLE"),
    Const(""),
    I18N("MEETING_CONFIRM_DELETE_STUDENT_NOTIF_APPENDIX", when="interesting_to_students"),
    Row(
        SwitchTo(I18N("COMMON_BTN_BACK"), id="cancel_delete", state=MeetingStates.info),
        Button(I18N("MEETING_CONFIRM_DELETE_BTN"), id="delete", when="can_be_deleted", on_click=on_delete_confirmed),
    ),
    state=MeetingStates.delete_confirm,
    getter=meeting_info_getter,
)
