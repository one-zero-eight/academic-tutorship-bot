from datetime import datetime
from typing import Literal

from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Back, Button, Row, ScrollingGroup
from aiogram_dialog.widgets.text import Const, Format

from src.bot.filters import *
from src.domain.models import *

BLANK_BUTTON = Button(Const(" "), id="blank")
BTN_ROW_BACK = Row(Back(), BLANK_BUTTON)


TEST_MEETINGS = [
    Meeting(status=CREATED, id=1, title="Prob&Stat Recap 3", date=1762983763, duration=3600),
    Meeting(
        status=CREATED,
        id=2,
        title="MathAn Recap 1",
        date=1762997763,
    ),
    Meeting(
        status=CREATED,
        id=3,
        title="Individual Maxim Pavlov",
        date=1762947763,
    ),
    Meeting(
        status=CREATED,
        id=4,
        title="OS PreFinal Preparation",
        date=1762947763,
    ),
    Meeting(
        status=CREATED,
        id=5,
        title="Optimization Last Recap",
    ),
]


class AdminStates(StatesGroup):
    menu = State("menu")
    meetings_type = State("meetings_type")
    meetings_list = State("meetings_list")
    create_meeting = State("create_meeting")
    meeting_info = State("meeting_info")


async def open_meetings_type_choice(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminStates.meetings_type)


admin_menu_ww: Window = Window(
    Const("Admin Panel"),
    Button(Const("Meetings"), id="a_meetings", on_click=open_meetings_type_choice),
    state=AdminStates.menu,
)


def open_meetings_list_of_type(type: Literal["created", "announced", "closed"]):
    async def open_meetings_list(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
        dialog_manager.dialog_data.update({"meetings_type": type})
        await dialog_manager.switch_to(AdminStates.meetings_list)

    return open_meetings_list


async def open_meeting_create(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminStates.create_meeting)


async def open_admin_menu(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(AdminStates.menu, mode=StartMode.RESET_STACK)


async def open_meeting_info(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    meeting_id = int(button.widget_id.replace("a_meeting_", ""))
    dialog_manager.dialog_data.update({"meeting": [x for x in TEST_MEETINGS if x.id == meeting_id][0]})
    await dialog_manager.switch_to(AdminStates.meeting_info)


HOME_BUTTON = Button(Const("Back"), id="admin_home", on_click=open_admin_menu)
BTN_ROW_HOME = Row(HOME_BUTTON, BLANK_BUTTON)


async def get_title_of_meeting(message: Message, _: MessageInput, dialog_manager: DialogManager):
    dialog_manager.dialog_data.update({"meeting": TEST_MEETINGS[0]})
    await dialog_manager.switch_to(AdminStates.meeting_info)


async def meetings_list_getter(dialog_manager: DialogManager, **kwargs):
    return {"meetings_type": str(dialog_manager.dialog_data["meetings_type"]).capitalize()}


async def meeting_info_getter(dialog_manager: DialogManager, **kwargs):
    data = dialog_manager.dialog_data
    meeting: Meeting = data["meeting"]
    date_to_str = lambda x: datetime.fromtimestamp(x).strftime("%d.%m.%Y")  # noqa E731
    duration_to_str = lambda x: f"{x // 3600:02d}:{(x % 3600) // 60:02d}"  # noqa E731
    return {
        "title": meeting.title,
        "description": meeting.description,
        "date": date_to_str(meeting.date) if meeting.date else "--.--.----",
        "duration": duration_to_str(meeting.duration) if meeting.duration else "--:--",
    }


omlot = open_meetings_list_of_type

admin_meetings_type_ww: Window = Window(
    Const("Meetings"),
    Row(Back(), Button(Const("Create New"), id="a_create_meeting", on_click=open_meeting_create)),
    Button(Const("See Created"), id="a_meetings_created", on_click=omlot("created")),
    Button(Const("See Announced"), id="a_meetings_announced", on_click=omlot("announced")),
    Button(Const("See Closed"), id="a_meetings_closed", on_click=omlot("closed")),
    state=AdminStates.meetings_type,
)

del omlot


def meeting_buttons(meetings: list[Meeting]) -> list[Button]:
    buttons = []
    for meeting in meetings:
        if meeting.date:
            date = datetime.fromtimestamp(meeting.date).strftime("%d.%m.%y")
        else:
            date = "-.-.-"
        if len(meeting.title) <= 25:
            title = meeting.title
        else:
            title = meeting.title[:14] + ".."
        buttons.append(Button(Const(f"[{date}] {title}"), id=f"a_meeting_{meeting.id}", on_click=open_meeting_info))
    return buttons


admin_meetings_list_ww: Window = Window(
    Format("{meetings_type} Meetings"),
    BTN_ROW_BACK,
    ScrollingGroup(
        *meeting_buttons(TEST_MEETINGS),
        id="a_meetings_list",
        width=1,
        height=3,
    ),
    state=AdminStates.meetings_list,
    getter=meetings_list_getter,
)


admin_create_meeting_ww = Window(
    Const("Create New Meeting"),
    Const("Enter Title:"),
    MessageInput(get_title_of_meeting),
    Row(Button(Const("Back"), id="create_back", on_click=open_meetings_type_choice), BLANK_BUTTON),
    state=AdminStates.create_meeting,
)

admin_meeting_info_ww = Window(
    Const("Meeting Info"),
    Format("{title}"),
    Format("Date: {date}"),
    Format("Duration: {duration}"),
    Format("{description}", when="description"),
    Row(Button(Const("Back"), id="back_window_info", on_click=open_meetings_type_choice), BLANK_BUTTON),
    state=AdminStates.meeting_info,
    getter=meeting_info_getter,
)

create_meeting: Window = ...

assign_tutor: Window = ...

router = Dialog(
    admin_menu_ww, admin_meetings_type_ww, admin_meetings_list_ww, admin_create_meeting_ww, admin_meeting_info_ww
)


@router.message(Command("admin"), StatusFilter("admin"))
async def open_menu(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(AdminStates.menu, mode=StartMode.RESET_STACK)
