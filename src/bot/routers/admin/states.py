from aiogram.fsm.state import State, StatesGroup


class AdminStates(StatesGroup):
    start = State("start")
    meetings_type = State("meetings_type")
    meetings_list = State("meetings_list")
    create_meeting = State("create_meeting")
    meeting_info = State("meeting_info")

    meeting_change = State("meeting_change")
    assign_tutor = State("assign_tutor")
    set_title = State("set_title")
    set_description = State("set_description")
    set_date = State("set_date")
    set_duration = State("set_duration")

    tutors_list = State("tutors_list")
    tutor_info = State("tutor_info")
    add_tutor = State("add_tutor")
