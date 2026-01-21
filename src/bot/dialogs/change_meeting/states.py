from aiogram.fsm.state import State, StatesGroup


class ChangeStates(StatesGroup):
    init = State()
    title = State()
    description = State()
    date = State()
    time = State()
    duration = State()
    tutor = State()
