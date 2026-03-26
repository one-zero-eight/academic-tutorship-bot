from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Cancel, Row, Start, SwitchTo
from aiogram_dialog.widgets.text import Const, Format

from src.bot.custom_widgets import MeetingInfoText
from src.bot.dialogs.tutors_profile import TutorProfileStates
from src.bot.dialogs.tutors_profile.handles import open_tutor_profile
from src.bot.filters import *
from src.bot.utils import COMMON_BACK_TEXT

from .dialog_buttons import *
from .getters import *
from .states import *

list_ww: Window = Window(
    Format("Upcoming Meetings"),
    MEETINGS_SCROLLING_GROUP,
    Row(Cancel(COMMON_BACK_TEXT, "cancel"), BLANK_BUTTON),
    state=StudentMeetingStates.list,
    getter=meetings_list_getter,
)


info_ww = Window(
    MeetingInfoText(),
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
    Row(SwitchTo(COMMON_BACK_TEXT, "to_list", StudentMeetingStates.list), BLANK_BUTTON),
    state=StudentMeetingStates.info,
    getter=meeting_info_getter,
)
