from aiogram_dialog.widgets.kbd import Back, Button, Row, ScrollingGroup, Select, SwitchTo
from aiogram_dialog.widgets.text import Const, Format

from src.bot.filters import *

from .handles import *

BTN_BLANK = Button(Const(" "), id="blank")
BTN_ROW_BACK = Row(Back(), BTN_BLANK)

BTN_INIT = SwitchTo(Const("Back"), id="to_init", state=ChangeStates.init, on_click=handle_clear)


TUTORS_ASSIGN_SCROLLING_GROUP = ScrollingGroup(
    Select(
        Format("@{item[1].username} {item[1].full_name}"),
        id="select_tutors",
        item_id_getter=(lambda item: item[1].id),
        items="tutors",
        on_click=on_tutor_assign,
    ),
    id="scroll_tutors",
    width=1,
    height=6,
    hide_pager=True,
)
"Unclickable, just to see the tutors"
