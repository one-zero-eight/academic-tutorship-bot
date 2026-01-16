from aiogram.fsm.state import State
from aiogram_dialog import ShowMode, StartMode
from aiogram_dialog.widgets.kbd import Back, Button, Row, ScrollingGroup, Select
from aiogram_dialog.widgets.text import Const, Format, Text

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


def StartWithData(
    text: Text,
    *,
    id: str,
    state: State,
    mode: StartMode = StartMode.NORMAL,
    show_mode: ShowMode = ShowMode.AUTO,
    when=None,
):
    """Start subdialog with whole dialog_data passed as start_data"""

    async def _handle(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
        data = dialog_manager.dialog_data.copy()
        return await dialog_manager.start(state=state, data=data, mode=mode, show_mode=show_mode)

    return Button(text=text, id=id, on_click=_handle, when=when)
