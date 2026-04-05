from aiogram.fsm.state import State, StatesGroup


class GuideStates(StatesGroup):
    language = State("language")
    init = State("init")
    disciplines = State("disciplines")
    disciplines_choose = State("disciplines_choose")
    notifications = State("notifications")
