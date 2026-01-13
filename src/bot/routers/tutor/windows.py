from aiogram_dialog import Window
from aiogram_dialog.widgets.text import Const, Format

from src.bot.filters import *
from src.domain.models import *

from .getters import *
from .states import *

start_ww = Window(
    Format("Hello there, {first_name} 👋"),
    Const("Tutor's panel"),
    getter=start_getter,
    state=TutorStates.start,
)
