from aiogram.fsm.state import State, StatesGroup


class DisciplineControlStates(StatesGroup):
    init = State()
    delete_submit = State()
