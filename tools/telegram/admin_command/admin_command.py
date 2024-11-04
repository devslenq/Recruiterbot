from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, Message, ReplyKeyboardRemove, CallbackQuery
from aiogram import F

from tools.database.localdatabase import LocalDatabase
from tools.database.model.database_models import Admin, Vacancy
from tools.telegram.admin_command.state.admin_state import AdminState
from tools.telegram.vacancy_command.vacancy_command import generate_city_keyboard, generate_vacancy_keyboard

admin_router = Router()
__database__ = LocalDatabase()

default_admin_id = 690546798
admin_list = [default_admin_id]


async def generate_admin_keyboard():
    keyboard = [
        [KeyboardButton(text="Добавить город")],
        [KeyboardButton(text="Добавить вакансии")],
        [KeyboardButton(text="Удалить вакансии")],
        [KeyboardButton(text="Добавить нового админа")],
        [KeyboardButton(text="Удалить админа")],
        [KeyboardButton(text="Посмотреть админов")],

    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


@admin_router.message(Command("admin"))
async def start_admin_panel(message: Message, state: FSMContext):
    global admin_list
    admin_list = await __database__.get_admins_list()
    if message.from_user.id not in admin_list:
        await state.clear()
        keyboard = await generate_admin_keyboard()
        await message.answer("Що будемо робити?", reply_markup=keyboard)


@admin_router.message(F.text.lower() == "добавить город")
async def process_callback_add_new_city(message: Message, state: FSMContext):
    await message.answer("Введiть имя города", reply_markup=ReplyKeyboardRemove())
    await state.set_state(AdminState.admin_add_new_city)

@admin_router.message(F.text.lower() == "добавить вакансии")
async def process_callback_add_new_city(message: Message, state: FSMContext):
    await message.answer("Введiть имя вакансии", reply_markup=ReplyKeyboardRemove())
    await state.set_state(AdminState.admin_add_new_vacancy)

@admin_router.message(F.text.lower() == "удалить вакансии")
async def process_callback_add_new_city(message: Message, state: FSMContext):
    keyboard = await generate_city_keyboard("admin_city_")
    await message.answer("Выбирайте город, из которого удалить вакансию", reply_markup=keyboard)
    await state.set_state(AdminState.admin_remove_vacancy)

@admin_router.callback_query(F.data.startswith('admin_city_'))
async def select_city(callback_query: CallbackQuery, state: FSMContext):
    city = callback_query.data.replace("admin_city_", "")
    print(city)
    vacancy_list = await __database__.get_vacancy_by_city(city)
    keyboard = await generate_vacancy_keyboard(vacancy_list, "admin_vacancy_")

    if vacancy_list or keyboard is None:
        print(f"xueta {keyboard}" )
        await callback_query.message.delete()
        await callback_query.message.answer(text="Выбирай вакансию, которую нужно удалить", reply_markup=keyboard)
    else:
        await callback_query.message.delete()
        await callback_query.message.answer(text="У цьому місті немає вакансій :(")
        await start_admin_panel(callback_query.message, state)

    await callback_query.answer()

@admin_router.callback_query(F.data.startswith('admin_vacancy_'))
async def remove_vacancy(callback_query: CallbackQuery, state: FSMContext):
    vacancy = callback_query.data.replace("admin_vacancy_", "")
    new_vacancy = await __database__.get_all_vacancies()
    for vacancy_new in new_vacancy:
        if str(vacancy_new.id).__contains__(vacancy):
            await __database__.delete_vacancy_by_id(vacancy_new.id)
            await callback_query.message.answer(text=f"Вакансию {vacancy_new.name} удалено")
            await state.clear()
            await start_admin_panel(callback_query.message, state)

    await callback_query.answer()

@admin_router.message(F.text.lower() == "добавить нового админа")
async def process_callback_add_new_admin(message: Message, state: FSMContext):
    await message.answer("Введiть id адмiна", reply_markup=ReplyKeyboardRemove())
    await state.set_state(AdminState.admin_add_new)


@admin_router.message(AdminState.admin_add_new_city)
async def add_new_city(message: Message, state: FSMContext):
    city = message.text
    await state.clear()
    await __database__.add_city(city)
    await message.answer(f"Ви успiшно добавили город {city}")
    await init_admin_command()
    await start_admin_panel(message, state)

@admin_router.message(AdminState.admin_remove_vacancy)
async def remove_vacancy_from_city(message: Message, state: FSMContext):
    city = message.text
    await state.clear()
    await __database__.add_city(city)
    await message.answer(f"Ви успiшно добавили город {city}")
    await init_admin_command()
    await start_admin_panel(message, state)

@admin_router.message(AdminState.admin_add_new_vacancy)
async def add_new_vacancy(message: Message, state: FSMContext):
    vacancy_name= message.text
    vacancy = Vacancy(name=vacancy_name)
    await __database__.add_vacancy(vacancy)
    await state.update_data({"vacancy": vacancy})
    await state.update_data({"vacancy_id": vacancy.id})
    from tools.telegram.vacancy_command.vacancy_command import generate_city_keyboard
    keyboard = await generate_city_keyboard("admin_city_")
    await message.answer("Выбери куда добавляем", reply_markup=keyboard)


@admin_router.callback_query(F.data.startswith('admin_city_'))
async def select_city(callback_query: CallbackQuery, state: FSMContext):
    userdata = await state.get_data()
    city = callback_query.data.replace("admin_city_", "")
    vacancy_id = userdata.get("vacancy_id")
    await __database__.add_city_to_vacancy(vacancy_id, city)
    await callback_query.message.answer(f"успешно добавлена вакансия в город {city}")
    await callback_query.answer()

@admin_router.message(AdminState.admin_add_new)
async def add_new_admin(message: Message, state: FSMContext):
    id = message.text
    await state.clear()
    await __database__.add_new_admin(Admin(telegram_id=id))
    await message.answer(f"Ви успiшно добавили адмiна з id {id}")
    global admin_list
    admin_list = await __database__.get_admins_list()
    await init_admin_command()
    await start_admin_panel(message, state)


@admin_router.message(F.text.lower() == "удалить админа")
async def process_callback_delete_admin(message: Message, state: FSMContext):
    await message.answer("Введiть id адмiна", reply_markup=ReplyKeyboardRemove())
    await state.set_state(AdminState.admin_remove)


@admin_router.message(AdminState.admin_remove)
async def remove_admin(message: Message, state: FSMContext):

    id = await state.get_data()
    await state.clear()
    await __database__.delete_admin_by_id(admin_id=id)
    await message.answer(f"Ви успiшно видалили адмiна з id {id}")
    await init_admin_command()
    await start_admin_panel(message, state)


@admin_router.message(F.text.lower() == "посмотреть админов")
async def process_callback_delete_admin(message: Message, state: FSMContext):
    admins_list = await __database__.get_admins_list()
    result = ""
    if admins_list:
        for admin in admins_list:
            result += f"{admin.telegram_id}\n"
    else:
        result = default_admin_id
    await message.answer(f"Id адмiнiв {result}")


async def init_admin_command():
    global admin_list
    admins = await __database__.get_admins_list()
    admin_list.clear()
    for admin in admins:
        admin_list.append(admin.id)
    admin_list.append(default_admin_id)
