from aiogram.fsm.state import State, StatesGroup


class RootStates(StatesGroup):
    start = State("start")
    settings = State("settings")
    settings_disciplines = State("settings_disciplines")
