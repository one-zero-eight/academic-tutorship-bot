from aiogram.fsm.state import State, StatesGroup


class AdminStates(StatesGroup):
    start = State("start")
