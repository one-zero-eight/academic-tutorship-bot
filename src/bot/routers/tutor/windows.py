from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Start
from aiogram_dialog.widgets.text import Const, Format

from src.bot.dialogs.meetings import MeetingStates
from src.bot.filters import *
from src.domain.models import *

from .getters import *
from .states import *

start_ww = Window(
    Format("Hello there, {first_name} 👋"),
    Const("Tutor's panel"),
    Start(Const("Meetings"), id="start_meetings", state=MeetingStates.type),
    getter=start_getter,
    state=TutorStates.start,
)
