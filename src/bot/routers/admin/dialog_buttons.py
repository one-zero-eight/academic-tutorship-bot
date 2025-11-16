from aiogram_dialog.widgets.kbd import Back, Button, Row, ScrollingGroup, Select
from aiogram_dialog.widgets.text import Const, Format

from src.bot.filters import *
from src.domain.models import *

from .handles import *

BLANK_BUTTON = Button(Const(" "), id="blank")
BTN_ROW_BACK = Row(Back(), BLANK_BUTTON)

HOME_BUTTON = Button(Const("Back"), id="admin_home", on_click=open_admin_menu)
BTN_ROW_HOME = Row(HOME_BUTTON, BLANK_BUTTON)

MEETINGS_SCROLLING_GROUP = ScrollingGroup(
    Select(
        Format("[{item.date_human}] {item.title}"),
        id="select_meetings",
        item_id_getter=(lambda x: TEST_MEETINGS.index(x)),
        items="meetings",
        on_click=on_meeting_selected,
    ),
    id="scroll_meetings",
    width=1,
    height=6,
)
