from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Cancel, Row, Start, SwitchTo
from aiogram_dialog.widgets.text import Format, List

from src.bot.custom_widgets import TutorProfileText
from src.bot.dialogs.discipline_picker.states import DisciplinePickerStates
from src.bot.filters import *
from src.bot.i18n import I18NFormat as I18N
from src.domain.models import *

from .dialog_buttons import *
from .getters import *
from .handles import *
from .states import *

profile_after_list_ww = Window(
    TutorProfileText(),
    Row(SwitchTo(I18N("COMMON_BTN_BACK"), id="back_to_list", state=TutorProfileStates.list), BLANK_BUTTON),
    getter=tutor_profile_getter,
    state=TutorProfileStates.profile_after_list,
)

profile_ww = Window(
    TutorProfileText(),
    Row(Cancel(I18N("COMMON_BTN_BACK"), id="close_profile"), BLANK_BUTTON),
    getter=tutor_profile_getter,
    state=TutorProfileStates.profile,
)

list_ww = Window(
    I18N("TUTOR_PROFILE_LIST_TITLE"),
    TUTORS_SCROLLING_GROUP,
    Row(Cancel(I18N("COMMON_BTN_BACK"), id="close_profile_list"), BLANK_BUTTON),
    getter=tutors_list_getter,
    state=TutorProfileStates.list,
)

profile_control_ww = Window(
    TutorProfileText(tutor_view=True),
    Row(
        SwitchTo(
            I18N("TUTOR_PROFILE_CONTROL_BTN_NAME"), id="to_profile_name", state=TutorProfileStates.set_profile_name
        ),
        SwitchTo(I18N("TUTOR_PROFILE_CONTROL_BTN_ABOUT"), id="to_about_text", state=TutorProfileStates.set_about),
    ),
    Row(
        # SwitchTo(Const("Photo"), id="to_profile_photo", state=TutorProfileStates.set_photo),
        SwitchTo(
            I18N("TUTOR_PROFILE_CONTROL_BTN_DISCIPLINES"),
            id="to_disciplines",
            state=TutorProfileStates.set_disciplines,
            on_click=on_open_disciplines,
        ),
    ),
    Row(Cancel(I18N("COMMON_BTN_BACK"), id="close_profile"), BLANK_BUTTON),
    getter=self_tutor_profile_getter,
    state=TutorProfileStates.profile_control,
)

set_profile_name_ww = Window(
    I18N("TUTOR_PROFILE_SET_NAME"),
    MessageInput(get_profile_name),
    Row(
        SwitchTo(I18N("COMMON_BTN_CANCEL"), id="back_to_profile", state=TutorProfileStates.profile_control),
        BLANK_BUTTON,
    ),
    state=TutorProfileStates.set_profile_name,
)

set_about_text_ww = Window(
    I18N("TUTOR_PROFILE_SET_ABOUT"),
    MessageInput(get_about_text),
    Row(
        SwitchTo(I18N("COMMON_BTN_CANCEL"), id="back_to_profile", state=TutorProfileStates.profile_control),
        BLANK_BUTTON,
    ),
    state=TutorProfileStates.set_about,
)

select_disciplines_ww = Window(
    I18N("TUTOR_PROFILE_SELECT_DISCIPLINES_TITLE"),
    List(Format("{item[display]}"), items="selected_disciplines"),
    Start(
        I18N("SETTINGS_DISCIPLINES_BTN_CHOOSE_OTHER"),
        id="start_select_disciplines",
        state=DisciplinePickerStates.language,
        data={"multi": True},
    ),
    SwitchTo(
        I18N("COMMON_BTN_SUBMIT"),
        id="back_to_profile",
        state=TutorProfileStates.profile_control,
        on_click=on_submit_disciplines,
    ),
    getter=selected_disciplines_getter,
    state=TutorProfileStates.set_disciplines,
)
