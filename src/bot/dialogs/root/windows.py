from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button, Row, Start, SwitchTo
from aiogram_dialog.widgets.text import Const, Format, List

from src.bot.dialogs.discipline_picker import DisciplinePickerStates
from src.bot.dialogs.discipline_picker.getters import selected_disciplines_getter
from src.bot.dialogs.meetings import MeetingStates
from src.bot.dialogs.student_meetings import StudentMeetingStates
from src.bot.dialogs.tutors import TutorsStates
from src.bot.dialogs.tutors_profile import TutorProfileStates
from src.bot.filters import *
from src.bot.utils import BLANK_BTN
from src.domain.models import *

from .getters import *
from .handles import *
from .states import *

TUTOR_START_APPENDIX = "🧑‍🏫 <i>Honorable tutor you are</i>"
ADMIN_START_APPENDIX = "👑 <i>And admin panel is also available for you</i>"

start_ww = Window(
    Format("Hello there, {first_name} 👋"),
    Const("Me, ArThur, will help you to keep track of upcoming AT meetings"),
    Const(" "),
    Const(TUTOR_START_APPENDIX, when="is_tutor"),
    Const(ADMIN_START_APPENDIX, when="is_admin"),
    # Students Buttons
    Row(
        Start(Const("📚 Upcoming Meetings"), id="start_meetings", state=StudentMeetingStates.list),
        Start(Const("🧑‍🏫 Tutors"), id="start_tutor_profiles", state=TutorProfileStates.list),
    ),
    SwitchTo(Const("⚙️ Settings"), "student_settings", state=RootStates.settings),
    # Tutors Buttons
    Row(
        Start(Const("🧑‍🏫 Your Meetings"), id="start_tutors_meetings", state=MeetingStates.type, when="is_tutor"),
        Start(
            Const("🧑‍🏫 Your Profile"),
            id="start_tutors_profile",
            state=TutorProfileStates.profile_control,
            when="is_tutor",
        ),
    ),
    # Admins Buttons
    Row(
        Start(Const("⚙️ Meetings Control"), id="start_all_meetings", state=MeetingStates.type, when="is_admin"),
        Start(Const("⚙️ Tutors Control"), id="start_tutors_control", state=TutorsStates.list, when="is_admin"),
    ),
    getter=start_getter,
    state=RootStates.start,
)


# TODO: move to separate settings dialog (issue #50)
settings_ww = Window(
    Const("⚙️ Settings️"),
    List(Format("- [{item[language]} {item[year]}y] {item[name]}"), items="relevant_disciplines"),
    Button(Format("Notifications: {receive_notifications}"), id="toggle_notif", on_click=on_toggle_notifications),
    SwitchTo(Const("Relevant Disciplines"), id="open_disciplines", state=RootStates.settings_disciplines),
    Row(SwitchTo(Const("Back"), id="to_start", state=RootStates.start), BLANK_BTN),
    getter=student_settings_getter,
    state=RootStates.settings,
)

select_disciplines_ww = Window(
    Const("📚 Selected Disciplines"),
    List(Format("- [{item[language]} {item[year]}y] {item[name]}"), items="selected_disciplines"),
    Start(
        Const("Choose other"),
        id="start_select_disciplines",
        state=DisciplinePickerStates.language,
        data={"multi": True},
    ),
    SwitchTo(Const("Submit"), id="back_to_profile", state=RootStates.settings, on_click=on_submit_disciplines),
    getter=selected_disciplines_getter,
    state=RootStates.settings_disciplines,
)
