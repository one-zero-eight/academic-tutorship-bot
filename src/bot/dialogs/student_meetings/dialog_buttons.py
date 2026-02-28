from aiogram_dialog.widgets.kbd import Back, Button, Row, ScrollingGroup, Select
from aiogram_dialog.widgets.text import Const, Format

from src.bot.dto import *
from src.bot.filters import *

from .handles import *

BLANK_BUTTON = Button(Const(" "), id="blank")
BTN_ROW_BACK = Row(Back(), BLANK_BUTTON)


MEETINGS_SCROLLING_GROUP = ScrollingGroup(
    Select(
        Format("[{item.date_human}] {item.title}"),
        id="select_meetings",
        item_id_getter=(lambda x: x.id),
        items="meetings",
        on_click=on_meeting_selected,
    ),
    id="scroll_meetings",
    width=1,
    height=6,
)
