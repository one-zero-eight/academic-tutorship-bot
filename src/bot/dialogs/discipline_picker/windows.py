from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Back, Cancel, Row, SwitchTo
from aiogram_dialog.widgets.text import Const

from src.bot.filters import *
from src.bot.utils import COMMON_BACK_TEXT, COMMON_CANCEL_TEXT

from .dialog_buttons import *
from .getters import *
from .handles import *
from .states import *

language_ww = Window(
    Const("Choose Program"),
    DISCIPLINE_LANGUAGE_SCROLL,
    Row(Cancel(COMMON_CANCEL_TEXT), BTN_BLANK, when="not_multi"),
    Row(Cancel(Const("Close")), BTN_BLANK, when="multi"),
    getter=languages_getter,
    state=DisciplinePickerStates.language,
)

year_ww = Window(
    Const("Choose Acadmic Year"),
    DISCIPLINE_YEAR_SCROLL,
    Row(Back(COMMON_BACK_TEXT), Cancel(COMMON_CANCEL_TEXT), when="not_multi"),
    Row(Back(COMMON_BACK_TEXT), Cancel(Const("Close")), when="multi"),
    getter=years_getter,
    state=DisciplinePickerStates.year,
)

discipline_ww = Window(
    Const("Choose Discipline"),
    DISCIPLINE_SCROLL,
    Row(Back(COMMON_BACK_TEXT), Cancel(COMMON_CANCEL_TEXT)),
    getter=disciplines_getter,
    state=DisciplinePickerStates.discipline,
)

discipline_multi_ww = Window(
    Const("Choose Disciplines"),
    DISCIPLINE_MULTI_SCROLL,
    Row(SwitchTo(COMMON_BACK_TEXT, id="to_year", state=DisciplinePickerStates.year), Cancel(Const("Close"))),
    getter=disciplines_multi_getter,
    state=DisciplinePickerStates.discipline_multi,
)
