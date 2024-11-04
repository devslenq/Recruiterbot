from aiogram.fsm.state import StatesGroup, State


class AdminState(StatesGroup):
    admin_add_new = State()
    admin_remove = State()
    admin_add_new_city = State()
    admin_add_new_vacancy = State()
    admin_remove_vacancy = State()