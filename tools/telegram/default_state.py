from aiogram.fsm.state import StatesGroup, State


class DefaultState(StatesGroup):
    send_admins_message = State()