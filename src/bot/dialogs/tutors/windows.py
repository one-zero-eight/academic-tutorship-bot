from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Cancel, Row, Start, SwitchTo

from src.bot.dialogs.tutors_profile import TutorProfileStates
from src.bot.filters import *
from src.bot.i18n import I18NFormat as I18N
from src.domain.models import *

from .dialog_buttons import *
from .getters import *
from .handles import *
from .states import *

list_ww = Window(
    I18N("TUTORS_ADMIN_LIST_TITLE"),
    TUTORS_SCROLLING_GROUP,
    Row(
        Cancel(I18N("COMMON_BTN_BACK")),
        SwitchTo(I18N("TUTORS_ADMIN_BTN_ADD_NEW"), id="to_add", state=TutorsStates.add, on_click=open_add_tutor),
    ),
    state=TutorsStates.list,
    getter=tutors_list_getter,
)


info_ww = Window(
    I18N("TUTORS_ADMIN_INFO"),
    Button(I18N("TUTORS_ADMIN_BTN_DISMISS"), id="rm_tutor", on_click=on_remove_tutor),
    Start(
        I18N("TUTORS_ADMIN_BTN_PROFILE"),
        id="open_profile",
        state=TutorProfileStates.profile,
        when="other_tutor_profile",
    ),
    Start(
        I18N("TUTORS_ADMIN_BTN_EDIT_PROFILE"),
        id="open_edit_profile",
        state=TutorProfileStates.profile_control,
        when="own_tutor_profile",
    ),
    Row(SwitchTo(I18N("COMMON_BTN_BACK"), id="to_list", state=TutorsStates.list), BLANK_BUTTON),
    state=TutorsStates.info,
    getter=tutor_info_getter,
    parse_mode="HTML",
)


admin_add_tutor_ww = Window(
    I18N("TUTORS_ADMIN_ADD_PROMPT"),
    Row(SwitchTo(I18N("COMMON_BTN_BACK"), id="to_list", state=TutorsStates.list, on_click=handle_clear), BLANK_BUTTON),
    MessageInput(get_added_tutor),
    state=TutorsStates.add,
)
