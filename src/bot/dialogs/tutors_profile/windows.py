from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Cancel, Row, Start, SwitchTo
from aiogram_dialog.widgets.text import Const, Format, List

from src.bot.custom_widgets import TutorProfileText
from src.bot.dialogs.discipline_picker.states import DisciplinePickerStates
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
    # TUTORS_SCROLLING_GROUP,
    getter=tutors_list_getter,
    state=TutorProfileStates.list,
)

profile_control_ww = Window(
    TutorProfileText(tutor_view=True),
    Row(
        SwitchTo(Const("Profile Name"), id="to_profile_name", state=TutorProfileStates.set_profile_name),
        SwitchTo(Const("About"), id="to_about_text", state=TutorProfileStates.set_about),
    ),
    Row(
        # SwitchTo(Const("Photo"), id="to_profile_photo", state=TutorProfileStates.set_photo),
        SwitchTo(
            Const("Disciplines"),
            id="to_disciplines",
            state=TutorProfileStates.set_disciplines,
            on_click=on_open_disciplines,
        ),
    ),
    Row(Cancel(Const("Back"), id="close_profile"), BLANK_BUTTON),
    getter=self_tutor_profile_getter,
    state=TutorProfileStates.profile_control,
)

set_profile_name_ww = Window(
    Const("Enter Profile Name"),
    Const("This name will be awailable to students"),
    MessageInput(get_profile_name),
    Row(SwitchTo(Const("Cancel"), id="back_to_profile", state=TutorProfileStates.profile_control), BLANK_BUTTON),
    state=TutorProfileStates.set_profile_name,
)

set_about_text_ww = Window(
    Const("Write something about you"),
    Const("This will be awailable to students"),
    MessageInput(get_about_text),
    Row(SwitchTo(Const("Cancel"), id="back_to_profile", state=TutorProfileStates.profile_control), BLANK_BUTTON),
    state=TutorProfileStates.set_about,
)

select_disciplines_ww = Window(
    Const("Selected Disciplines"),
    List(Format("({item[language]} {item[year]}y.) {item[name]}"), items="selected_disciplines"),
    Start(
        Const("Choose other"),
        id="start_select_disciplines",
        state=DisciplinePickerStates.language,
        data={"multi": True},
    ),
    SwitchTo(
        Const("Submit"), id="back_to_profile", state=TutorProfileStates.profile_control, on_click=on_submit_disciplines
    ),
    getter=selected_disciplines_getter,
    state=TutorProfileStates.set_disciplines,
)
