from aiogram.fsm.state import State, StatesGroup


class MeetingStates(StatesGroup):
    type = State()
    list = State()
    info = State()
    create = State()
    announce_confirm = State()
    delete_confirm = State()
