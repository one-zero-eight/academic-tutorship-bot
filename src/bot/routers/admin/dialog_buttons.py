from datetime import datetime

from aiogram_dialog.widgets.kbd import Back, Button, Row
from aiogram_dialog.widgets.text import Const

from src.bot.filters import *
from src.domain.models import *

from .handles import *

BLANK_BUTTON = Button(Const(" "), id="blank")
BTN_ROW_BACK = Row(Back(), BLANK_BUTTON)

HOME_BUTTON = Button(Const("Back"), id="admin_home", on_click=open_admin_menu)
BTN_ROW_HOME = Row(HOME_BUTTON, BLANK_BUTTON)


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
