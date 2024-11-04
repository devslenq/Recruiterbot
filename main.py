import asyncio
import os

import dotenv

from tools.telegram.telegramhelper import start_bot

dotenv.load_dotenv()

asyncio.run(start_bot())