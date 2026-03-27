from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Back, Cancel, Row, SwitchTo

from src.bot.filters import *
from src.bot.i18n import I18NFormat as I18N

from .dialog_buttons import *
from .getters import *
from .handles import *
from .states import *

language_ww = Window(
    I18N("DISCIPLINE_PICKER_LANGUAGE_TITLE"),
    DISCIPLINE_LANGUAGE_SCROLL,
    Row(Cancel(I18N("COMMON_BTN_CANCEL")), BTN_BLANK, when="not_multi"),
    Row(Cancel(I18N("COMMON_BTN_CLOSE")), BTN_BLANK, when="multi"),
    getter=languages_getter,
    state=DisciplinePickerStates.language,
)

year_ww = Window(
    I18N("DISCIPLINE_PICKER_YEAR_TITLE"),
    DISCIPLINE_YEAR_SCROLL,
    Row(Back(I18N("COMMON_BTN_BACK")), Cancel(I18N("COMMON_BTN_CANCEL")), when="not_multi"),
    Row(Back(I18N("COMMON_BTN_BACK")), Cancel(I18N("COMMON_BTN_CLOSE")), when="multi"),
    getter=years_getter,
    state=DisciplinePickerStates.year,
)

discipline_ww = Window(
    I18N("DISCIPLINE_PICKER_DISCIPLINE_TITLE"),
    DISCIPLINE_SCROLL,
    Row(Back(I18N("COMMON_BTN_BACK")), Cancel(I18N("COMMON_BTN_CANCEL"))),
    getter=disciplines_getter,
    state=DisciplinePickerStates.discipline,
)

discipline_multi_ww = Window(
    I18N("DISCIPLINE_PICKER_DISCIPLINES_TITLE"),
    DISCIPLINE_MULTI_SCROLL,
    Row(
        SwitchTo(I18N("COMMON_BTN_BACK"), id="to_year", state=DisciplinePickerStates.year),
        Cancel(I18N("COMMON_BTN_CLOSE")),
    ),
    getter=disciplines_multi_getter,
    state=DisciplinePickerStates.discipline_multi,
)
