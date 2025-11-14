from aiogram.fsm.state import State, StatesGroup


class AdminStates(StatesGroup):
    menu = State("menu")
    meetings_type = State("meetings_type")
    meetings_list = State("meetings_list")
    create_meeting = State("create_meeting")
    meeting_info = State("meeting_info")
    assign_tutor = State("assign_tutor")
    confirm_tutor = State("confirm_tutor")
