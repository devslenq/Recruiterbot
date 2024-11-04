from aiogram.fsm.state import StatesGroup, State


class MainMenu(StatesGroup):
    about_company = State()
    vacancy = State()