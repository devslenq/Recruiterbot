from aiogram.fsm.state import StatesGroup, State


class Welcome(StatesGroup):
    name = State()
