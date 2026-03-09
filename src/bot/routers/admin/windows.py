from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Start
from aiogram_dialog.widgets.text import Const

from src.bot.dialogs.meetings import MeetingStates
from src.bot.dialogs.tutors import TutorsStates
from src.bot.dialogs.tutors_profile import TutorProfileStates
from src.bot.filters import *
from src.bot.utils import user_status_getter
from src.domain.models import *

from .states import *

admin_start_ww: Window = Window(
    Const("Admin Panel"),
    Start(Const("Meetings"), id="start_meetings", state=MeetingStates.type),
    Start(Const("Tutors"), id="start_tutors", state=TutorsStates.list),
    Start(Const("Profile"), id="start_tutors_profile", state=TutorProfileStates.profile_control, when="is_tutor"),
    state=AdminStates.start,
    getter=user_status_getter,
)
