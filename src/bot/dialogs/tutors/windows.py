from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Cancel, Row, Start, SwitchTo
from aiogram_dialog.widgets.text import Const, Format

from src.bot.dialogs.tutors_profile import TutorProfileStates
from src.bot.filters import *
from src.domain.models import *

from .dialog_buttons import *
from .getters import *
from .handles import *
from .states import *

list_ww = Window(
    Const("Tutors List"),
    TUTORS_SCROLLING_GROUP,
    Row(
        Cancel(Const("Back")),
        SwitchTo(Const("Add New"), id="to_add", state=TutorsStates.add, on_click=open_add_tutor),
    ),
    state=TutorsStates.list,
    getter=tutors_list_getter,
)


info_ww = Window(
    Format("Tutor [{id}] Info"),
    Format("{full_name}"),
    Format("@{username}"),
    Format("telegram id: <code>{telegram_id}</code>"),
    Button(Const("Dismiss"), id="rm_tutor", on_click=on_remove_tutor),
    Start(Const("Profile"), id="open_profile", state=TutorProfileStates.profile, when="profile_set"),
    Row(SwitchTo(Const("Back"), id="to_list", state=TutorsStates.list), BLANK_BUTTON),
    state=TutorsStates.info,
    getter=tutor_info_getter,
    parse_mode="HTML",
)


admin_add_tutor_ww = Window(
    Const("Share contact of the new Tutor"),
    Row(SwitchTo(Const("Back"), id="to_list", state=TutorsStates.list, on_click=handle_clear), BLANK_BUTTON),
    MessageInput(get_added_tutor),
    state=TutorsStates.add,
)
