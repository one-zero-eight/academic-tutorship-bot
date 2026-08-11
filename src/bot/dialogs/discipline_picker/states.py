from aiogram.fsm.state import State, StatesGroup


class DisciplinePickerStates(StatesGroup):
    language = State()
    year = State()
    semester = State()
    discipline = State()
    discipline_multi = State()
