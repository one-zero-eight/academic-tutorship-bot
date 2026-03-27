from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button, Url
from aiogram_dialog.widgets.text import Format

from src.bot.i18n import I18NFormat as I18N

from .getters import *
from .handles import *
from .states import *

bind_ww = Window(
    I18N("AUTH_BIND_INSTRUCTION"),
    Url(I18N("AUTH_BTN_CONNECT_TELEGRAM"), url=Format("{binding_url}")),
    Button(I18N("AUTH_BTN_CHECK_CONNECTED"), id="check_connected", on_click=check_connected),
    state=AuthStates.bind_tg_inh,
    getter=start_getter,
)
