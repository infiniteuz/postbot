import os
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from dotenv import load_dotenv

load_dotenv()

# Barcha routerlarni import qilamiz
from handlers.start import start_router
from handlers.post_creation import post_creation_router
from handlers.button_handlers import button_router
from handlers.reply_handlers import reply_router
from handlers.inline_mode import inline_router
from handlers.edit_handlers import edit_router
from handlers.language_handlers import language_router
from handlers.admin_handlers import admin_router
from handlers.help_handlers import help_router
from utils.database import init_db, keep_awake

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

def setup_bot():
    """Botni ishga tushirish uchun barcha sozlamalarni bajaradi"""
    logging.basicConfig(level=logging.INFO)
    init_db()
    keep_awake()  # Botni uxlamasligi uchun
    
    # Routerlarni dispatcherga ulaymiz
    dp.include_router(start_router)
    dp.include_router(post_creation_router)
    dp.include_router(button_router)
    dp.include_router(reply_router)
    dp.include_router(inline_router)
    dp.include_router(edit_router)
    dp.include_router(language_router)
    dp.include_router(admin_router)
    dp.include_router(help_router)
    
    print("Bot muvaffaqiyatli sozlandi!")
