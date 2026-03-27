from aiogram_dialog.widgets.kbd import Back, Row, ScrollingGroup, Select
from aiogram_dialog.widgets.text import Format

from src.bot.filters import *
from src.bot.utils import BLANK_BTN

from .handles import *

BLANK_BUTTON = BLANK_BTN
BTN_ROW_BACK = Row(Back(), BLANK_BUTTON)


MEETINGS_SCROLLING_GROUP = ScrollingGroup(
    Select(
        Format("{item[display]}"),
        id="select_meetings",
        item_id_getter=(lambda item: item["id"]),
        items="meetings",
        on_click=on_meeting_selected,
    ),
    id="scroll_meetings",
    width=1,
    height=6,
)
