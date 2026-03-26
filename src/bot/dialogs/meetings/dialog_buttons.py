from aiogram.fsm.state import State
from aiogram_dialog import ShowMode, StartMode
from aiogram_dialog.widgets.kbd import Back, Button, Row, ScrollingGroup, Select
from aiogram_dialog.widgets.text import Format, Text

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
