from aiogram.fsm.state import State, StatesGroup


class TutorProfileStates(StatesGroup):
    list = State()
    profile_after_list = State()
    profile = State()

    profile_control = State()
    set_profile_name = State()
    set_disciplines = State()
    set_about = State()
    set_photo = State()
