from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram_dialog.widgets.text import Const, Format

from src.bot.filters import *
from src.domain.models import *

from .getters import *
from .states import *

start_ww = Window(
    Format("Hello there, {first_name} 👋"),
    SwitchTo(Const("Meetings List"), "student_meetings_list", state=StudentStates.meetings_list),
    SwitchTo(Const("Settings"), "student_settings", state=StudentStates.settings),
    getter=start_getter,
    state=StudentStates.start,
)

settings_ww = Window(Const("Student Settings ⚙️"), state=StudentStates.settings)
