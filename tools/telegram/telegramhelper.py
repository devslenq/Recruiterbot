import logging
import os

from aiogram import Dispatcher, Bot
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from tools.database.localdatabase import LocalDatabase
from tools.database.model.database_models import User
from tools.locale.localehelper import LocaleHelper

__dp__ = Dispatcher()
__database__ = LocalDatabase()

from tools.telegram.admin_command.admin_command import admin_router, init_admin_command

from tools.telegram.main_menu_command.main_menu_command import main_menu_router, main_menu
from tools.telegram.vacancy_command.vacancy_command import vacancy_router

from tools.telegram.welcome_commands.state.welcome_state import Welcome

from tools.telegram.welcome_commands.welcome_commands import welcome_router

logging.basicConfig(level=logging.INFO)

__dp__.include_router(welcome_router)
__dp__.include_router(main_menu_router)
__dp__.include_router(vacancy_router)
__dp__.include_router(admin_router)


@__dp__.message(CommandStart())
async def __start__(message: Message, state: FSMContext):
    await state.clear()
    user = await __database__.get_user_by_id(message.from_user.id)
    if not user:
        user = User(telegram_id=message.from_user.id, username=message.from_user.username)
        await __database__.add_new_user(user)
        await state.set_state(Welcome.name)
        await message.answer("""STYLUS Вітає.\nМи раді, що Ви вирішили доєднатись до нашої компанії.\nЦей бот створено для того, щоб ви швидше та легше знаходили актуальні вакансії саме для Вас.
        \nДавайте знайомитись! Напиши своє ім'я""")
    else:
        await main_menu(message)


locale_helper = LocaleHelper("russian")
bot = Bot(os.getenv('TELEGRAM_TOKEN'))


async def start_bot():
    await __dp__.start_polling(bot)
    await init_admin_command()
