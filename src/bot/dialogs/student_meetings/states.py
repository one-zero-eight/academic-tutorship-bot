from aiogram.fsm.state import State, StatesGroup


class StudentMeetingStates(StatesGroup):
    list = State()
    info = State()
