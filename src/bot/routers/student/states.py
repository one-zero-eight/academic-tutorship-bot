from aiogram.fsm.state import State, StatesGroup


class StudentStates(StatesGroup):
    start = State("start")
    meetings_list = State("meetings_list")
    settings = State("settings")
