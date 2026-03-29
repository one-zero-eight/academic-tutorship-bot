from aiogram.fsm.state import State, StatesGroup


class ChangeStates(StatesGroup):
    init = State()
    title = State()
    title_discipline = State()
    description = State()
    date_room = State()
    room = State()
    date = State()
    time = State()
    duration = State()
    tutor = State()
    save_approve = State()
    back_approve = State()
