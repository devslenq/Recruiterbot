import re
from time import sleep

from aiogram import F
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup, \
    ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tools.database.localdatabase import LocalDatabase
from tools.telegram.vacancy_command.state.vacancy_state import VacancyState

vacancy_router = Router()
__database__ = LocalDatabase()


async def generate_city_keyboard(prefix = "city_"):
    cities = await __database__.get_all_cities()
    print(cities)
    keyboard_builder = InlineKeyboardBuilder()
    for city in cities:
        keyboard_builder.add(InlineKeyboardButton(text=city.name, callback_data=f"{prefix}{city.name}"))
    keyboard_builder.adjust(2)
    return keyboard_builder.as_markup()


async def generate_vacancy_keyboard(vacancy_list, prefix = "vacancy_"):
    keyboard_builder = InlineKeyboardBuilder()
    for vacancy in vacancy_list:
        print(vacancy)
        keyboard_builder.add(InlineKeyboardButton(text=vacancy.name, callback_data=f"{prefix}{vacancy.id}"))

    if not keyboard_builder.buttons:
        return None
    keyboard_builder.adjust(2)
    return keyboard_builder.as_markup()


async def generate_personal_data_keyboard():
    keyboard = [
        [KeyboardButton(text="Я даю дозвіл на використання моїх персональних даних")],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


async def init_vacancy_command(message: Message):
    keyboard = await generate_city_keyboard()
    await message.answer("Обери своє місто, а ми надамо актуальні вакансії!", reply_markup=keyboard)


@vacancy_router.callback_query(F.data.startswith('city_'))
async def select_city(callback_query: CallbackQuery, state: FSMContext):
    city = callback_query.data.replace("city_", "")
    print(city)
    await state.update_data({"select_city": city})
    vacancy_list = await __database__.get_vacancy_by_city(city)
    keyboard = await generate_vacancy_keyboard(vacancy_list)
    if vacancy_list:
        await callback_query.message.delete()
        await callback_query.message.answer(text="Обирай найкрутішу вакансію 😎", reply_markup=keyboard)
    else:
        await callback_query.message.delete()
        await callback_query.message.answer(text="У цьому місті немає вакансій :(")
        from tools.telegram.main_menu_command.main_menu_command import main_menu
        await main_menu(message=callback_query.message)

    await callback_query.answer()


@vacancy_router.callback_query(F.data.startswith('vacancy_'))
async def select_vacancy(callback_query: CallbackQuery, state: FSMContext):
    vacancy = callback_query.data.replace("vacancy_", "")
    await state.update_data({"vacancy_id": vacancy})
    personal_data_keyboard = await generate_personal_data_keyboard()
    await callback_query.message.delete()
    await callback_query.message.answer(text="Чудово!")
    sleep(1)
    await callback_query.message.answer(text="Залишилось ще трохи...")
    sleep(1)
    await callback_query.message.answer(text="Щоб з тобою зв'язатись , нам потрібні твої дані")
    sleep(1)
    await callback_query.message.answer(
        text="""Про те перш ніж запитувати тебе , згідно закону України "Про захист персональних даних" ми повинні отримати згоду на зберігання та обробку персональних даних.""",
        reply_markup=personal_data_keyboard
    )

    await callback_query.answer()


@vacancy_router.message(F.text.lower() == "я даю дозвіл на використання моїх персональних даних")
async def process_callback_go_to_main_menu(message: Message, state: FSMContext):
    await message.delete()
    await message.answer("Чудово! Ви дали доступ на використання персональних даних.")
    sleep(1)
    await message.answer("Напишіть, будь ласка, рік свого народження. \nФормат : 2001", reply_markup=ReplyKeyboardRemove())
    await state.set_state(VacancyState.birthday)


@vacancy_router.message(VacancyState.birthday)
async def birthday(message: Message, state: FSMContext):
    user_input = message.text

    # Удаление пробелов из введенного текста
    filtered_input = user_input.replace(" ", "")

    # Проверка на соответствие формату: 4 цифры
    if re.fullmatch(r'\d{4}', filtered_input):
        # await state.clear()
        await state.update_data({"birthday": filtered_input})
        keyboard = [
            [KeyboardButton(text="Залишити контакт", request_contact=True)],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)
        await message.answer(text="А для швидкого зв'язку , залиш свій контакт", reply_markup=reply_markup)
        await state.set_state(VacancyState.contact)
    else:
        await message.answer(text="Некоректна дата. Спробуй знову")


@vacancy_router.message(VacancyState.contact)
async def contacts(message: Message, state: FSMContext):
    if message.contact is None:
        keyboard = [
            [KeyboardButton(text="Залишити контакт", request_contact=True)],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)
        await message.answer(text ="Ви не дали нам свiй контакт, тому не зможемо зв'язатися.\nНадайте контакт, ну будь ласка :)", reply_markup=reply_markup )
        return
    user_data = await state.get_data()
    print(user_data)
    birthday = user_data.get("birthday")
    select_city = user_data.get("select_city")
    vacancy = user_data.get("vacancy_id")
    vacancy_name = await __database__.get_vacancy_by_id(vacancy)
    await state.clear()
    await message.answer(f"Дякуємо тобі!\nНаша команда зв'яжеться з тобою у найближчий час",
                         reply_markup=ReplyKeyboardRemove())
    from tools.telegram.admin_command.admin_command import admin_list
    for list in admin_list:
        from tools.telegram.telegramhelper import bot
        await bot.send_message(chat_id=list,
                               text=f"Пользователь {message.from_user.username}\nОткликнулся на вакансию: {vacancy_name}\nВ городе {select_city}\nГод рождения {birthday}\nномер телефона {message.contact.phone_number}")
