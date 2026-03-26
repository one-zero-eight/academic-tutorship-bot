from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Cancel, Next, Row, Start, SwitchTo
from aiogram_dialog.widgets.text import Const, Format

from src.bot.custom_widgets import MeetingInfoText
from src.bot.dialogs.attendance.states import AttendanceStates
from src.bot.dialogs.change_meeting.states import ChangeStates
from src.bot.dialogs.discipline_picker.states import DisciplinePickerStates
from src.bot.dialogs.tutors_profile.handles import open_tutor_profile
from src.bot.dialogs.tutors_profile.states import TutorProfileStates
from src.bot.filters import *
from src.bot.i18n import I18NFormat as I18N
from src.bot.utils import COMMON_BACK_TEXT, COMMON_CANCEL_TEXT

from .dialog_buttons import *
from .getters import *
from .handles import *
from .states import *

omlot = open_meetings_list_of_type

type_ww: Window = Window(
    I18N("Meeting-Type-Head"),
    Row(
        Cancel(I18N("Back")),
        SwitchTo(I18N("New-Meeting-Btn"), id="create_meeting", state=MeetingStates.create),
    ),
    Button(I18N("Type-Created-Btn"), id="a_meetings_created", on_click=omlot("created"), when="can_see_created"),
    Button(
        I18N("Type-Approving-Btn"), id="a_meetings_approving", on_click=omlot("approving"), when="can_see_approving"
    ),
    Button(
        I18N("Type-Announced-Btn"), id="a_meetings_announced", on_click=omlot("announced"), when="can_see_announced"
    ),
    Button(I18N("Type-Closed-Btn"), id="a_meetings_closed", on_click=omlot("closed"), when="can_see_closed"),
    state=MeetingStates.type,
    getter=meetings_type_getter,
)

del omlot


list_ww: Window = Window(
    Format("{meetings_type} Meetings"),
    MEETINGS_SCROLLING_GROUP,
    Row(SwitchTo(I18N("Back"), "to_type", MeetingStates.type), BLANK_BUTTON),
    state=MeetingStates.list,
    getter=meetings_list_getter,
)

create_ww = Window(
    I18N("New-Meeting-Head"),
    Format("Title: {title}"),
    Format("Discipline: {discipline_name}"),
    Row(
        Next(Const("Title")),
        Start(Const("Discipline"), id="choose_discipline", state=DisciplinePickerStates.language),
    ),
    Row(
        SwitchTo(COMMON_BACK_TEXT, "to_type", MeetingStates.type),
        Button(Const(" "), id="blank", when="cannot_be_created"),
        Button(Const("Create ✅"), id="create_submit", on_click=on_create_submit, when="can_be_created"),
    ),
    getter=meeting_create_getter,
    state=MeetingStates.create,
)

create_enter_title_ww = Window(
    Const("Create New Meeting"),
    Format("Discipline: {discipline_name}"),
    Const("Enter Title:"),
    MessageInput(get_new_title),
    Row(SwitchTo(COMMON_BACK_TEXT, "to_type", MeetingStates.type), BLANK_BUTTON),
    getter=meeting_create_getter,
    state=MeetingStates.create_title,
)


info_ww = Window(
    MeetingInfoText(admin_info=True),
    Start(
        text=Const("Change Info"),
        id="change_init",
        state=ChangeStates.init,
        show_mode=ShowMode.EDIT,
        when="can_be_changed",
    ),
    Button(
        Const("Tutor Profile"),
        id="to_tutor_profile",
        when="can_see_tutor_profile",
        on_click=open_tutor_profile,
    ),
    Start(
        Const("To Your Profile"),
        id="to_tutor_profile_control",
        state=TutorProfileStates.profile_control,
        when="can_see_tutor_profile_control",
    ),
    Button(Const("Announce"), id="announce_start", on_click=open_announce_confirm, when="can_be_announced"),
    Button(
        Const("Send for Approval"),
        id="approval_start",
        on_click=open_send_for_approval_confirm,
        when="can_be_sent_for_approval",
    ),
    Button(Const("Finish"), id="finish_start", on_click=open_finish_confirm, when="can_be_finished"),
    Start(Const("Close"), id="start_close", state=AttendanceStates.close, when="can_be_closed"),
    Start(Const("Attendance"), id="start_attendance", state=AttendanceStates.init, when="can_see_attendance"),
    SwitchTo(
        Const("Cancel Meeting"), id="cancel_meeting_start", state=MeetingStates.delete_confirm, when="can_be_deleted"
    ),
    Row(SwitchTo(COMMON_BACK_TEXT, "to_list", MeetingStates.list), BLANK_BUTTON),
    state=MeetingStates.info,
    getter=meeting_info_getter,
)


send_for_approval_confirm_ww = Window(
    Format('Are you surely ready to send "{title}" for approval?'),
    Const("After approval, the meeting will be <u>announced automatically</u>."),
    Row(
        Button(
            Const("Send for Approval 📩"),
            id="send_for_approval",
            when="can_be_sent_for_approval",
            on_click=on_send_for_approval_confirmed,
        ),
        SwitchTo(COMMON_CANCEL_TEXT, id="cancel_send_for_approval", state=MeetingStates.info),
    ),
    state=MeetingStates.send_for_approval_confirm,
    getter=meeting_info_getter,
)


announce_confirm_ww = Window(
    Format('Are you surely ready to announce "{title}"?'),
    Row(
        Button(Const("Announce 📣"), id="announce", when="can_be_announced", on_click=on_announce_confirmed),
        SwitchTo(COMMON_CANCEL_TEXT, id="cancel_announce", state=MeetingStates.info),
    ),
    state=MeetingStates.announce_confirm,
    getter=meeting_info_getter,
)


finish_confirm_ww = Window(
    Format('Are you surely ready to finish "{title}"?'),
    Row(
        Button(Const("Finish ☑️"), id="finish", when="can_be_finished", on_click=on_finish_confirmed),
        SwitchTo(COMMON_CANCEL_TEXT, id="cancel_finish", state=MeetingStates.info),
    ),
    state=MeetingStates.finish_confirm,
    getter=meeting_info_getter,
)


delete_confirm_ww = Window(
    Format('Do you really want to cancel "{title}"?'),
    Const("This action cannot be undone and the meeting will be deleted."),
    Const(""),
    Const("The notification will be sent to students 💌.", when="interesting_to_students"),
    Row(
        Button(Const("Cancel Meeting 🗑️"), id="delete", when="can_be_deleted", on_click=on_delete_confirmed),
        SwitchTo(COMMON_CANCEL_TEXT, id="cancel_delete", state=MeetingStates.info),
    ),
    state=MeetingStates.delete_confirm,
    getter=meeting_info_getter,
)
