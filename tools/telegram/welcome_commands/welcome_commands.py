import re

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from tools.database.localdatabase import LocalDatabase
from tools.telegram.admin_command.admin_command import start_admin_panel
from tools.telegram.main_menu_command.main_menu_command import main_menu
from tools.telegram.welcome_commands.state.welcome_state import Welcome

welcome_router = Router()
__database__ = LocalDatabase()


def is_valid_name(name: str) -> bool:
    return bool(re.fullmatch(r"^[a-zA-Zа-яА-ЯёЁ]+$", name))


@welcome_router.message(Welcome.name)
async def welcome(message: Message, state: FSMContext):
    if message.text == "/admin":
        await state.clear()
        await start_admin_panel(message, state)
    if is_valid_name(message.text):
        await state.clear()
        await __database__.update_name_user(message.from_user.id, message.text)
        await message.answer(f"Приємно познайомитись, {message.text}")
        await main_menu(message)
    else:
        await message.answer(f"Щось не так із твоїм ім'ям. Давай спробуємо заново")
        await state.clear()
        await state.set_state(Welcome.name)
