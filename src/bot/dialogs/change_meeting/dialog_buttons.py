from aiogram_dialog.widgets.kbd import Back, Row, ScrollingGroup, Select, SwitchTo
from aiogram_dialog.widgets.text import Format

from src.bot.filters import *
from src.bot.utils import BLANK_BTN, COMMON_BACK_TEXT

from .handles import *

BTN_BLANK = BLANK_BTN
BTN_ROW_BACK = Row(Back(), BTN_BLANK)

BTN_INIT = SwitchTo(COMMON_BACK_TEXT, id="to_init", state=ChangeStates.init, on_click=handle_clear)


TUTORS_ASSIGN_SCROLLING_GROUP = ScrollingGroup(
    Select(
        Format("{item[1][display]}"),
        id="select_tutors",
        item_id_getter=(lambda item: item[1]["id"]),
        items="tutors",
        on_click=on_tutor_assign,
    ),
    id="scroll_tutors",
    width=1,
    height=6,
    hide_pager=True,
)
"Unclickable, just to see the tutors"
