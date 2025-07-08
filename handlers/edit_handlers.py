import logging
from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from states.post_states import PostCreation
from keyboards.reply import get_post_settings_kb, get_cancel_kb
from keyboards.inline import generate_post_keyboard
from utils.database import get_post_from_db, update_post_in_db

edit_router = Router()

@edit_router.message(F.text == "📝 Post tahrirlash")
async def ask_for_post_code(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(PostCreation.waiting_for_edit_code)
    await message.answer(
        "Tahrirlamoqchi bo'lgan postingizning noyob kodini yuboring:",
        reply_markup=get_cancel_kb()
    )

@edit_router.message(PostCreation.waiting_for_edit_code, F.text)
async def load_post_for_editing(message: types.Message, state: FSMContext):
    post_code = message.text.strip()
    post_info = get_post_from_db(post_code)

    if not post_info:
        await message.answer("Bunday kodli post topilmadi. Qaytadan urinib ko'ring yoki /cancel ni bosing.")
        return

    if post_info['user_id'] != message.from_user.id:
        await message.answer("Kechirasiz, siz faqat o'zingiz yaratgan postlarni tahrirlay olasiz.")
        return

    post_data = post_info.get('post_content')
    buttons_list = post_info.get('buttons_list', [])

    await state.set_data({
        "post_data": post_data,
        "buttons_list": buttons_list,
        "post_code_to_edit": post_code
    })

    await state.set_state(PostCreation.configuring_post)

    keyboard = generate_post_keyboard(buttons_list) if post_data.get('content_type') in ('text', 'photo', 'video') else None

    try:
        content_type = post_data.get('content_type')
        chat_id = message.chat.id

        file_id = post_data.get("file_id")
        caption = post_data.get("caption")
        text = post_data.get("text")

        if content_type == 'text':
            sent_message = await message.bot.send_message(chat_id, text, reply_markup=keyboard)
        elif content_type == 'photo':
            sent_message = await message.bot.send_photo(chat_id, file_id, caption=caption, reply_markup=keyboard)
        elif content_type == 'video':
            sent_message = await message.bot.send_video(chat_id, file_id, caption=caption, reply_markup=keyboard)
        else:
             await message.answer("Bu turdagi postni tahrirlash hozircha qo'llab-quvvatlanmaydi.")
             await state.clear()
             return

        new_post_data = await state.get_data()
        new_post_data['post_data']['message_id'] = sent_message.message_id
        await state.set_data(new_post_data)

    except Exception as e:
        logging.error(f"Postni tahrirlash uchun yuklashda xatolik: {e}")
        await message.answer("Postni yuklashda xatolik yuz berdi.")
        return

    await message.answer(f"`{post_code}` kodli post tahrirlash uchun yuklandi.",
                         reply_markup=get_post_settings_kb(), parse_mode="Markdown")

@edit_router.message(PostCreation.configuring_post, F.text == "✅ Done")
async def done_post_editing(message: types.Message, state: FSMContext):
    data = await state.get_data()
    post_data = data.get("post_data")
    buttons_matrix = data.get("buttons_matrix", [])
    post_code = data.get("post_code_to_edit")
    
    if not post_data or not post_code:
        return await message.answer("Xatolik: Saqlash uchun post topilmadi.")

    try:
        update_post_in_db(post_code, post_data, buttons_matrix)
    except Exception as e:
        logging.error(f"DBga saqlashda xatolik: {e}")
        return await message.answer("Postni saqlashda xatolik yuz berdi.")

    await state.clear()
    await message.answer(
        f"☑️ Post `{post_code}` kodi bilan muvaffaqiyatli yangilandi!",
        reply_markup=get_main_menu(), parse_mode="Markdown"
    )
