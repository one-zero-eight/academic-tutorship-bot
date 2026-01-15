from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Back, Button, Row, ScrollingGroup, Select
from aiogram_dialog.widgets.text import Const, Format
from db.repositories import meetings_repo

from src.bot.dto import *
from src.bot.filters import *


class MeetingStates(StatesGroup):
    list = State()
    info = State()


async def on_meeting_selected(query: CallbackQuery, widget: Any, dialog_manager: DialogManager, item_id: str):
    meeting = await meetings_repo.get(id=int(item_id))
    dialog_manager.dialog_data.update({"meeting": meeting_to_dto(meeting)})
    await dialog_manager.switch_to(MeetingStates.info)


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
