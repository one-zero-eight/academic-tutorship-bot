from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Cancel, Row, Start, SwitchTo

from src.bot.custom_widgets import MeetingInfoText
from src.bot.dialogs.tutors_profile import TutorProfileStates
from src.bot.dialogs.tutors_profile.handles import open_tutor_profile
from src.bot.filters import *
from src.bot.i18n import I18NFormat as I18N

from .dialog_buttons import *
from .getters import *
from .states import *

list_ww: Window = Window(
    I18N("STUDENT_MEETINGS_LIST_TITLE"),
    MEETINGS_SCROLLING_GROUP,
    Row(Cancel(I18N("COMMON_BTN_BACK"), "cancel"), BLANK_BUTTON),
    state=StudentMeetingStates.list,
    getter=meetings_list_getter,
)


info_ww = Window(
    MeetingInfoText(),
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
    Row(SwitchTo(I18N("COMMON_BTN_BACK"), "to_list", StudentMeetingStates.list), BLANK_BUTTON),
    state=StudentMeetingStates.info,
    getter=meeting_info_getter,
)
