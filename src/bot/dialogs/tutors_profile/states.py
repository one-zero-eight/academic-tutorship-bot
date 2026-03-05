from aiogram.fsm.state import State, StatesGroup


class TutorProfileStates(StatesGroup):
    list = State()
    profile_after_list = State()
    profile = State()
