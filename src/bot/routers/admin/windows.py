from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Row, Start, SwitchTo
from aiogram_dialog.widgets.text import Const, Format

from src.bot.dialogs.meetings import MeetingStates
from src.bot.filters import *
from src.domain.models import *

from .dialog_buttons import *
from .getters import *
from .handles import *
from .states import *

admin_start_ww: Window = Window(
    Const("Admin Panel"),
    Start(Const("Meetings"), id="start_meetings", state=MeetingStates.type),
    SwitchTo(Const("Tutors"), id="a_tutors", state=AdminStates.tutors_list),
    state=AdminStates.start,
)

admin_tutors_list_ww = Window(
    Const("Tutors List"),
    TUTORS_SCROLLING_GROUP,
    Row(
        HOME_BUTTON,
        Button(Const("Add New"), id="add_tutor", on_click=open_add_tutor),
    ),
    state=AdminStates.tutors_list,
    getter=tutors_list_getter,
)


admin_tutor_info_ww = Window(
    Format("Tutor [{id}] Info"),
    Format("{full_name}"),
    Format("@{username}"),
    Format("telegram id: <code>{tg_id}</code>"),
    Button(Const("Dismiss"), id="rm_tutor", on_click=on_remove_tutor),
    Row(SwitchTo(Const("Back"), id="back_window_change", state=AdminStates.tutors_list), BLANK_BUTTON),
    state=AdminStates.tutor_info,
    getter=tutor_info_getter,
    parse_mode="HTML",
)


admin_add_tutor_ww = Window(
    Const("Share contact of the new Tutor"),
    Row(Button(Const("Back"), id="back_add_tutor", on_click=open_tutors_list_with_clear), BLANK_BUTTON),
    MessageInput(get_added_tutor),
    state=AdminStates.add_tutor,
)
