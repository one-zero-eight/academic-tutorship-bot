from aiogram.fsm.state import State, StatesGroup


class TutorsStates(StatesGroup):
    list = State()
    info = State()
    add = State()
    delete = State()
