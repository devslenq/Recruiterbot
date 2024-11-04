from time import sleep

from aiogram import Router, F, types
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from tools.database.localdatabase import LocalDatabase

main_menu_router = Router()
__database__ = LocalDatabase()

__about_company__ = """Мрієте працювати з технікою, яка змінює життя? У Stylus.ua ми розуміємо, що техніка – це більше, ніж просто пристрої.
Інтернет-магазин Stylus існує на українському ринку онлайн-продажів з 2008 року, і за цей час встиг зарекомендувати себе як надійний інтернет-магазин та партнер. 
На даний момент під знаком для товари та послуги STYLUS працює більше 10 фірмових магазинів, сервісний центр у м. Київ та більше [15 точок видачі товарів](https://robota.ua/redirect?event_name=url_click&redir_token=eyJPcmlnaW5hbFVybCI6Imh0dHBzOi8vc3R5bHVzLnVhL3VrL2NvbnRhY3RzLmh0bWwiLCJWYWNhbmN5SWQiOjEwMTU1MzQ4fQ==) по Україні."""


def main_menu_keyboard():
    keyboard = [
        [types.KeyboardButton(text="Про компанію")],
        [types.KeyboardButton(text="Вакансії")]
    ]

    return types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def back_to_main_menu_keyboard():
    keyboard = [
        [types.KeyboardButton(text="Повернутися до головного меню")],
    ]

    return types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


async def main_menu(message: Message, state: FSMContext = None):
    if state:
        await state.clear()
    await message.answer("Обирай те, що важливіше", reply_markup=main_menu_keyboard())


@main_menu_router.message(F.text.lower() == "про компанію")
async def process_callback_about_company_button(message: Message):

    await message.answer(__about_company__, parse_mode=ParseMode.MARKDOWN, reply_markup=back_to_main_menu_keyboard())


@main_menu_router.message(F.text.lower() == "вакансії")
async def process_callback_vacancy(message: Message, state: FSMContext):
    await message.answer(
        "Ми працюємо по всій Україні. Тому можемо запропонувати вакансії майже у кожному куточку України.",
        reply_markup=ReplyKeyboardRemove())
    sleep(1.5)
    from tools.telegram.vacancy_command.vacancy_command import init_vacancy_command
    await init_vacancy_command(message)


@main_menu_router.message(F.text.lower() == "повернутися до головного меню")
async def process_callback_go_to_main_menu(message: Message):
    await main_menu(message)
