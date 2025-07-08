from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_main_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="✍️ Post yaratish"), KeyboardButton(text="📝 Post tahrirlash"))
    builder.row(KeyboardButton(text="⚙️ Til sozlamalari"))
    return builder.as_markup(resize_keyboard=True)

def get_cancel_kb():
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="❌ Bekor qilish"))
    return builder.as_markup(resize_keyboard=True)

def get_post_settings_kb(web_preview_disabled: bool = False):
    builder = ReplyKeyboardBuilder()
    options_text = "Preview: OFF" if web_preview_disabled else "Preview: ON"
    
    builder.row(
        KeyboardButton(text="👁️‍🗨️ Preview"),
        KeyboardButton(text=options_text),
        KeyboardButton(text="🔡 Get Buttons"),
        KeyboardButton(text="✏️ Edit Content")
    )
    builder.row(
        KeyboardButton(text="❌ Cancel"),
        KeyboardButton(text="✅ Done")
    )
    return builder.as_markup(resize_keyboard=True)

def get_language_selection_kb():
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="🇺🇿 O'zbek tili"))
    builder.row(KeyboardButton(text="🇬🇧 English"))
    builder.row(KeyboardButton(text="🇷🇺 Русский"))
    builder.row(KeyboardButton(text="◀️ Orqaga"))
    return builder.as_markup(resize_keyboard=True)
