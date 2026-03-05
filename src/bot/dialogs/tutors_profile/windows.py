from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Cancel, Row, SwitchTo
from aiogram_dialog.widgets.text import Const

from src.bot.custom_widgets import TutorProfileText
from src.bot.filters import *
from src.domain.models import *

from .dialog_buttons import *
from .getters import *
from .handles import *
from .states import *

profile_after_list_ww = Window(
    TutorProfileText(),
    Row(SwitchTo(Const("Back"), id="back_to_list", state=TutorProfileStates.list), BLANK_BUTTON),
    getter=tutor_profile_getter,
    state=TutorProfileStates.profile_after_list,
)

profile_ww = Window(
    TutorProfileText(),
    Row(Cancel(Const("Back"), id="close_profile"), BLANK_BUTTON),
    getter=tutor_profile_getter,
    state=TutorProfileStates.profile,
)

list_ww = Window(
    Const("🧑‍🏫 Here are all of your Tutors!"),
    TUTORS_SCROLLING_GROUP,
    getter=tutors_list_getter,
    state=TutorProfileStates.list,
)
