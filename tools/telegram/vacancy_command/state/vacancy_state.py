from aiogram.fsm.state import StatesGroup, State


class VacancyState(StatesGroup):
    city = State()
    vacancy = State()
    user_data = State()
    concordance = State()
    birthday = State()
    contact = State()