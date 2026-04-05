from aiogram.fsm.state import State, StatesGroup


class AttendanceStates(StatesGroup):
    init = State()
    resend = State()
    add_email = State()
    close = State()
