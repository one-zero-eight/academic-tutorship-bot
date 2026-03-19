from aiogram_dialog.widgets.kbd import Button, ScrollingGroup, Select
from aiogram_dialog.widgets.text import Const, Format

from src.bot.filters import *

from .handles import *

BLANK_BUTTON = Button(Const(" "), id="blank")

TUTORS_SCROLLING_GROUP = ScrollingGroup(
    Select(
        Format("{item[1].profile_name} @{item[1].username}"),
        id="select_tutors",
        item_id_getter=(lambda item: item[1].id),
        items="tutors",
        on_click=on_tutor_selected,
    ),
    id="scroll_tutors",
    width=1,
    height=6,
)
