from aiogram_dialog.widgets.kbd import ScrollingGroup, Select
from aiogram_dialog.widgets.text import Format

from src.bot.utils import BLANK_BTN

from .handles import *

BTN_BLANK = BLANK_BTN


DISCIPLINE_LANGUAGE_SCROLL = ScrollingGroup(
    Select(
        Format("{item[1]}"),
        id="select_language",
        item_id_getter=(lambda item: item[0]),
        items="languages",
        on_click=on_language_select,
    ),
    id="scroll_language",
    width=1,
    height=10,
    hide_pager=True,
)


DISCIPLINE_YEAR_SCROLL = ScrollingGroup(
    Select(
        Format("{item[1]}"),
        id="select_year",
        item_id_getter=(lambda item: item[0]),
        items="years",
        on_click=on_year_select,
    ),
    id="scroll_year",
    width=1,
    height=15,
    hide_pager=True,
)


DISCIPLINE_SCROLL = ScrollingGroup(
    Select(
        Format("{item[1][display]}"),
        id="select_discipline",
        item_id_getter=(lambda item: item[0]),
        items="disciplines",
        on_click=on_discipline_select,
    ),
    id="scroll_year",
    width=1,
    height=30,
    hide_pager=True,
)


DISCIPLINE_MULTI_SCROLL = ScrollingGroup(
    Select(
        Format("{item[2]} {item[1][display]}"),
        id="select_discipline",
        item_id_getter=(lambda item: item[0]),
        items="disciplines_multi",
        on_click=on_discipline_select_multi,
    ),
    id="scroll_year",
    width=1,
    height=30,
    hide_pager=True,
)
