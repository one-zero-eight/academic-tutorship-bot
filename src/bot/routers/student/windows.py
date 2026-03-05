from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Start, SwitchTo
from aiogram_dialog.widgets.text import Const, Format

from src.bot.dialogs.student_meetings import StudentMeetingStates
from src.bot.dialogs.tutors_profile import TutorProfileStates
from src.bot.filters import *
from src.domain.models import *

from .getters import *
from .states import *

start_ww = Window(
    Format("Hello there, {first_name} 👋"),
    Start(Const("Meetings"), id="start_meetings", state=StudentMeetingStates.list),
    Start(Const("Tutors"), id="start_tutor_profiles", state=TutorProfileStates.list),
    SwitchTo(Const("Settings"), "student_settings", state=StudentStates.settings),
    getter=start_getter,
    state=StudentStates.start,
)

settings_ww = Window(Const("Student Settings ⚙️"), state=StudentStates.settings)
