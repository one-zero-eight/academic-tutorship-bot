from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Back, Button, Cancel, Next, Row, Start
from aiogram_dialog.widgets.text import Const, Format, List

from src.bot.dialogs.discipline_picker import DisciplinePickerStates
from src.bot.dialogs.discipline_picker.getters import selected_disciplines_getter
from src.bot.dialogs.root.handles import on_submit_disciplines
from src.bot.filters import *
from src.bot.utils import BLANK_BTN
from src.domain.models import *

from .getters import *
from .handles import *
from .states import *

INIT_TEXT = """
Hello student!
Me name is ArThur, I am the bot of Academic Tutorship (AT for short).

The system helps to keep track of meetings (recaps, consultations) on various university disciplines of your choice.
"""


DISCIPLINES_TEXT = """
You may choose the disciplines you're interested in.

Or skip and do that later in ⚙️ <b>Settings</b>.
"""


NOTIFICATIONS_TEXT = """
The big part of my value are notifications about upcoming meetings.

We send notifications in different bot
Please activate it 👇 to continue
🔗 <a href="{link}"><i>Academic Notifications Bot</i></a>

(you may block notifications in ⚙️ Settings)
"""

init_ww = Window(
    Format(INIT_TEXT),
    Row(
        BLANK_BTN,
        Next(Const("Next ➡️")),
    ),
    state=GuideStates.init,
)


disciplines_ww = Window(
    Format(DISCIPLINES_TEXT),
    Const(" "),
    Const("📚 No disciplines selected yet", when="nothing_chosen"),
    Const("📚 Selected Disciplines", when="something_chosen"),
    List(Format("- [{item[language]} {item[year]}y] {item[name]}"), items="selected_disciplines"),
    Start(
        Const("Choose"),
        id="start_select_disciplines",
        state=DisciplinePickerStates.language,
        data={"multi": True},
        when="nothing_chosen",
    ),
    Start(
        Const("Choose other"),
        id="start_select_disciplines",
        state=DisciplinePickerStates.language,
        data={"multi": True},
        when="something_chosen",
    ),
    Row(
        Back(Const("⬅️ Back")),
        Next(Const("Next ➡️"), on_click=on_submit_disciplines, when="something_chosen"),
        Next(Const("Skip ➡️"), on_click=on_submit_disciplines, when="nothing_chosen"),
    ),
    getter=selected_disciplines_getter,
    state=GuideStates.disciplines,
)


notifications_ww = Window(
    Format(NOTIFICATIONS_TEXT),
    Row(
        Back(Const("⬅️ Back")),
        Cancel(Const("Finish guide 🎉"), when="bot_activated", on_click=set_saw_guide_true),
        Button(Const(" "), id="blank", when="not_bot_activated"),
    ),
    getter=notification_state_getter,
    state=GuideStates.notifications,
)
