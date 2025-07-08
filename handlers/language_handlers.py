from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from keyboards.reply import get_language_selection_kb, get_main_menu
from utils.database import set_user_language

language_router = Router()

@language_router.message(F.text == "⚙️ Til sozlamalari")
async def language_settings(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Iltimos, kerakli tilni tanlang:", 
                         reply_markup=get_language_selection_kb())

@language_router.message(F.text.in_(["🇺🇿 O'zbek tili", "🇬🇧 English", "🇷🇺 Русский"]))
async def select_language(message: types.Message, state: FSMContext):
    lang_map = {
        "🇺🇿 O'zbek tili": "uz",
        "🇬🇧 English": "en",
        "🇷🇺 Русский": "ru"
    }
    
    selected_lang = lang_map.get(message.text, "uz")
    set_user_language(message.from_user.id, selected_lang)
    
    confirmation = {
        "uz": "Til muvaffaqiyatli o'zgartirildi!",
        "en": "Language successfully changed!",
        "ru": "Язык успешно изменен!"
    }
    
    await message.answer(confirmation.get(selected_lang, "Til o'zgartirildi"),
                         reply_markup=get_main_menu())
