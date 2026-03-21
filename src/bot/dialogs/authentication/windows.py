from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button, Url
from aiogram_dialog.widgets.text import Const, Format

from .getters import *
from .handles import *
from .states import *

bind_ww = Window(
    Const(
        "To proceed, please connect "
        "your telegram with your InNoHassle account "
        'by pressing the button "Connect Telegram 🔗"'
        "\n\n"
        'After that press "Check Connected ✅"'
    ),
    Url(Const("Connect Telegram 🔗"), url=Format("{binding_url}")),
    Button(Const("Check Connected ✅"), id="check_connected", on_click=check_connected),
    state=AuthStates.bind_tg_inh,
    getter=start_getter,
)
