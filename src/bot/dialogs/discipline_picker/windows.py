from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Back, Cancel, Row, SwitchTo
from aiogram_dialog.widgets.text import Const

from src.bot.filters import *

from .dialog_buttons import *
from .getters import *
from .handles import *
from .states import *

language_ww = Window(
    Const("Choose Program"),
    DISCIPLINE_LANGUAGE_SCROLL,
    Row(Cancel(Const("Cancel")), BTN_BLANK, when="not_multi"),
    Row(Cancel(Const("Close")), BTN_BLANK, when="multi"),
    getter=languages_getter,
    state=DisciplinePickerStates.language,
)

year_ww = Window(
    Const("Choose Acadmic Year"),
    DISCIPLINE_YEAR_SCROLL,
    Row(Back(Const("Back")), Cancel(Const("Cancel")), when="not_multi"),
    Row(Back(Const("Back")), Cancel(Const("Close")), when="multi"),
    getter=years_getter,
    state=DisciplinePickerStates.year,
)

discipline_ww = Window(
    Const("Choose Discipline"),
    DISCIPLINE_SCROLL,
    Row(Back(Const("Back")), Cancel(Const("Cancel"))),
    getter=disciplines_getter,
    state=DisciplinePickerStates.discipline,
)

discipline_multi_ww = Window(
    Const("Choose Disciplines"),
    DISCIPLINE_MULTI_SCROLL,
    Row(SwitchTo(Const("Back"), id="to_year", state=DisciplinePickerStates.year), Cancel(Const("Close"))),
    getter=disciplines_multi_getter,
    state=DisciplinePickerStates.discipline_multi,
)
