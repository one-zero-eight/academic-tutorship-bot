from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Cancel, Row, SwitchTo
from aiogram_dialog.widgets.text import Const

from src.bot.custom_widgets.disciplines_control_list_text import DisciplinesControlListText
from src.bot.filters import *
from src.bot.i18n import I18NFormat as I18N

from .getters import *
from .handles import *
from .states import *

init_ww = Window(
    I18N("DISCIPLINES_CONTROL_INIT"),
    Const("\n"),
    DisciplinesControlListText(),
    Const("\n"),
    I18N("DISCIPLINES_CONTROL_INIT_INSTRUCTIONS"),
    Row(
        Cancel(I18N("COMMON_BTN_BACK")),
        SwitchTo(I18N("COMMON_BTN_RELOAD"), id="reload", state=DisciplineControlStates.init),
    ),
    getter=disciplines_getter,
    state=DisciplineControlStates.init,
)
