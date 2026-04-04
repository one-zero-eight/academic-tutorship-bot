from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Back, Button, Cancel, Next, Row, Start
from aiogram_dialog.widgets.text import Const

from src.bot.custom_widgets import UnpackedList
from src.bot.dialogs.discipline_picker import DisciplinePickerStates
from src.bot.dialogs.discipline_picker.getters import selected_disciplines_getter
from src.bot.dialogs.root.handles import on_submit_disciplines
from src.bot.filters import *
from src.bot.i18n import I18NFormat as I18N
from src.bot.utils import BLANK_BTN
from src.domain.models import *

from .getters import *
from .handles import *
from .states import *

language_ww = Window(
    I18N("GUIDE_LANGUAGE_TEXT"),
    Row(
        Button(I18N("GUIDE_LANGUAGE_BTN_EN"), id="guide_lang_en", on_click=on_choose_language_en),
        Button(I18N("GUIDE_LANGUAGE_BTN_RU"), id="guide_lang_ru", on_click=on_choose_language_ru),
    ),
    state=GuideStates.language,
)


init_ww = Window(
    I18N("GUIDE_INIT_TEXT"),
    Row(
        BLANK_BTN,
        Next(I18N("GUIDE_BTN_NEXT")),
    ),
    state=GuideStates.init,
)


disciplines_ww = Window(
    I18N("GUIDE_DISCIPLINES_TEXT"),
    Const(" "),
    I18N("GUIDE_DISCIPLINES_NONE_SELECTED", when="nothing_chosen"),
    I18N("GUIDE_DISCIPLINES_SELECTED_TITLE", when="something_chosen"),
    UnpackedList(I18N("SETTINGS_DISCIPLINE_ITEM"), items="selected_disciplines"),
    Start(
        I18N("SETTINGS_DISCIPLINES_BTN_CHOOSE"),
        id="start_select_disciplines",
        state=DisciplinePickerStates.language,
        data={"multi": True},
        when="nothing_chosen",
    ),
    Start(
        I18N("SETTINGS_DISCIPLINES_BTN_CHOOSE_OTHER"),
        id="start_select_disciplines",
        state=DisciplinePickerStates.language,
        data={"multi": True},
        when="something_chosen",
    ),
    Row(
        Back(I18N("GUIDE_BTN_BACK")),
        Next(I18N("GUIDE_BTN_NEXT"), on_click=on_submit_disciplines, when="something_chosen"),
        Next(I18N("GUIDE_BTN_SKIP"), on_click=on_submit_disciplines, when="nothing_chosen"),
    ),
    getter=selected_disciplines_getter,
    state=GuideStates.disciplines,
)


notifications_ww = Window(
    I18N("GUIDE_NOTIFICATIONS_TEXT"),
    Row(
        Back(I18N("GUIDE_BTN_BACK")),
        Cancel(I18N("GUIDE_BTN_FINISH"), when="bot_activated", on_click=set_saw_guide_true),
        Button(Const(" "), id="blank", when="not_bot_activated"),
    ),
    getter=notification_state_getter,
    state=GuideStates.notifications,
)
