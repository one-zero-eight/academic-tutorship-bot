from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button, Row, Start, SwitchTo
from aiogram_dialog.widgets.text import Const, Format, List

from src.bot.dialogs.discipline_picker import DisciplinePickerStates
from src.bot.dialogs.discipline_picker.getters import selected_disciplines_getter
from src.bot.dialogs.student_meetings import StudentMeetingStates
from src.bot.dialogs.tutors_profile import TutorProfileStates
from src.bot.filters import *
from src.bot.utils import BLANK_BTN
from src.domain.models import *

from .getters import *
from .handles import *
from .states import *

start_ww = Window(
    Format("Hello there, {first_name} 👋"),
    Start(Const("Meetings"), id="start_meetings", state=StudentMeetingStates.list),
    Start(Const("Tutors"), id="start_tutor_profiles", state=TutorProfileStates.list),
    SwitchTo(Const("Settings"), "student_settings", state=StudentStates.settings),
    getter=start_getter,
    state=StudentStates.start,
)

settings_ww = Window(
    Const("Student Settings ⚙️"),
    List(Format("- [{item[language]} {item[year]}y] {item[name]}"), items="relevant_disciplines"),
    Button(Format("Notifications: {receive_notifications}"), id="toggle_notif", on_click=on_toggle_notifications),
    SwitchTo(Const("Relevant Disciplines"), id="open_disciplines", state=StudentStates.settings_disciplines),
    Row(SwitchTo(Const("Back"), id="to_start", state=StudentStates.start), BLANK_BTN),
    getter=student_settings_getter,
    state=StudentStates.settings,
)

select_disciplines_ww = Window(
    Const("Selected Disciplines"),
    List(Format("- [{item[language]} {item[year]}y] {item[name]}"), items="selected_disciplines"),
    Start(
        Const("Choose other"),
        id="start_select_disciplines",
        state=DisciplinePickerStates.language,
        data={"multi": True},
    ),
    SwitchTo(Const("Submit"), id="back_to_profile", state=StudentStates.settings, on_click=on_submit_disciplines),
    getter=selected_disciplines_getter,
    state=StudentStates.settings_disciplines,
)
