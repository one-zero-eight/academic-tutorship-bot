from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button, Row, Start, SwitchTo
from aiogram_dialog.widgets.text import Const

from src.bot.custom_widgets import UnpackedList
from src.bot.dialogs.discipline_picker import DisciplinePickerStates
from src.bot.dialogs.discipline_picker.getters import selected_disciplines_getter
from src.bot.dialogs.meetings import MeetingStates
from src.bot.dialogs.student_meetings import StudentMeetingStates
from src.bot.dialogs.tutors import TutorsStates
from src.bot.dialogs.tutors_profile import TutorProfileStates
from src.bot.filters import *
from src.bot.i18n import I18NFormat as I18N
from src.bot.utils import BLANK_BTN
from src.domain.models import *

from .getters import *
from .handles import *
from .states import *

start_ww = Window(
    I18N("ROOT_START_STUDENT"),
    Const(" "),
    I18N("ROOT_START_TUTOR_APPENDIX", when="is_tutor"),
    I18N("ROOT_START_ADMIN_APPENDIX", when="is_admin"),
    # Students Buttons
    Row(
        Start(I18N("ROOT_BTN_UPCOMING_MEETINGS"), id="start_meetings", state=StudentMeetingStates.list),
        Start(I18N("ROOT_BTN_TUTORS"), id="start_tutor_profiles", state=TutorProfileStates.list),
    ),
    SwitchTo(I18N("ROOT_BTN_SETTINGS"), "student_settings", state=RootStates.settings),
    # Tutors Buttons
    Row(
        Start(I18N("ROOT_BTN_YOUR_MEETINGS"), id="start_tutors_meetings", state=MeetingStates.type, when="is_tutor"),
        Start(
            I18N("ROOT_BTN_YOUR_PROFILE"),
            id="start_tutors_profile",
            state=TutorProfileStates.profile_control,
            when="is_tutor",
        ),
    ),
    # Admins Buttons
    Row(
        Start(I18N("ROOT_BTN_MEETINGS_CONTROL"), id="start_all_meetings", state=MeetingStates.type, when="is_admin"),
        Start(I18N("ROOT_BTN_TUTORS_CONTROL"), id="start_tutors_control", state=TutorsStates.list, when="is_admin"),
    ),
    getter=start_getter,
    state=RootStates.start,
)


# TODO: move to separate settings dialog (issue #50)
settings_ww = Window(
    I18N("SETTINGS_HEADING"),
    UnpackedList(I18N("SETTINGS_DISCIPLINE_ITEM"), items="relevant_disciplines"),
    Const(" "),
    Button(I18N("SETTINGS_LANG_TOGGLE"), id="toggle_lang", on_click=on_toggle_language),
    I18N("SETTINGS_NOTIFICATIONS_LINK"),
    I18N("SETTINGS_NOTIF_UNACTIVATED", when="notification_bot_unactivated"),
    I18N("SETTINGS_NOTIF_BLOCKED", when="notification_bot_blocked"),
    Button(I18N("SETTINGS_NOTIF_TOGGLE"), id="toggle_notif", on_click=on_toggle_notifications),
    SwitchTo(I18N("SETTINGS_BTN_CHANGE_DISCIPLINES"), id="open_disciplines", state=RootStates.settings_disciplines),
    Row(SwitchTo(I18N("COMMON_BTN_BACK"), id="to_start", state=RootStates.start), BLANK_BTN),
    getter=student_settings_getter,
    state=RootStates.settings,
)

select_disciplines_ww = Window(
    I18N("SETTINGS_DISCIPLINES_TITLE"),
    UnpackedList(I18N("SETTINGS_DISCIPLINE_ITEM"), items="selected_disciplines"),
    Start(
        I18N("SETTINGS_DISCIPLINES_BTN_CHOOSE_OTHER"),
        id="start_select_disciplines",
        state=DisciplinePickerStates.language,
        data={"multi": True},
    ),
    SwitchTo(
        I18N("COMMON_BTN_SUBMIT"), id="back_to_profile", state=RootStates.settings, on_click=on_submit_disciplines
    ),
    getter=selected_disciplines_getter,
    state=RootStates.settings_disciplines,
)
