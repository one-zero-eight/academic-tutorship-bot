from aiogram.fsm.state import State, StatesGroup
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const


class AdminStates(StatesGroup):
    menu = State("menu")


admin_menu_ww = Window(
    Const("Admin menu"),
    Button(Const("Just a Admin Button"), id="button"),
    state=AdminStates.menu,
)

router = Dialog(admin_menu_ww, name="admin")
