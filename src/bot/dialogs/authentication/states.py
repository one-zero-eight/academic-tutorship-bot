from aiogram.fsm.state import State, StatesGroup


class AuthStates(StatesGroup):
    bind_tg_inh = State("bind_telegram_to_innohassle")
