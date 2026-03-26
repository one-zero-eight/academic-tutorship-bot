from aiogram_dialog.widgets.kbd import ScrollingGroup, Select
from aiogram_dialog.widgets.text import Format

from src.bot.filters import *
from src.bot.utils import BLANK_BTN

from .handles import *

BLANK_BUTTON = BLANK_BTN

TUTORS_SCROLLING_GROUP = ScrollingGroup(
    Select(
        Format("{item[1][display]}"),
        id="select_tutors",
        item_id_getter=(lambda item: item[1]["id"]),
        items="tutors",
        on_click=on_tutor_selected,
    ),
    id="scroll_tutors",
    width=1,
    height=6,
)
