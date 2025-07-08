import logging
from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.media_group import MediaGroupBuilder

from states.post_states import PostCreation
from keyboards.reply import get_main_menu, get_cancel_kb, get_post_settings_kb
from keyboards.inline import generate_preview_keyboard
from utils.database import add_post_to_db

reply_router = Router()

# "⚙️ Options" tugmasi
@reply_router.message(PostCreation.configuring_post, F.text.startswith("Preview:"))
async def options_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    is_disabled = data.get('disable_web_page_preview', False)
    new_state = not is_disabled
    await state.update_data(disable_web_page_preview=new_state)
    status_text = "o'chirildi" if new_state else "yoqildi"
    await message.answer(f"🔗 URL oldindan ko'rish {status_text}.",
                         reply_markup=get_post_settings_kb(web_preview_disabled=new_state))

# "🔡 Get Buttons" tugmasi
@reply_router.message(PostCreation.configuring_post, F.text == "🔡 Get Buttons")
async def get_buttons_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    buttons_matrix = data.get("buttons_matrix", [])

    # Matritsada haqiqiy tugma borligini tekshirish
    has_real_buttons = any(any(btn and not btn.get('is_placeholder') for btn in row) for row in buttons_matrix)

    if not has_real_buttons:
        return await message.answer("Siz hali hech qanday tugma qo'shmadingiz.")

    response_text = "Sizning tugmalaringiz:\n\n"
    button_count = 1
    for row in buttons_matrix:
        for button in row:
            if button and not button.get('is_placeholder'):
                response_text += f"{button_count}. {button['text']} = {button['url']}\n"
                button_count += 1
    await message.answer(response_text)

# "✏️ Edit Content" tugmasi
@reply_router.message(PostCreation.configuring_post, F.text == "✏️ Edit Content")
async def edit_content_handler(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(PostCreation.waiting_for_content)
    await message.answer("Yangi post yaratish boshlandi. Iltimos, yangi tarkibni yuboring.",
                         reply_markup=get_cancel_kb())

# "👁️‍🗨️ Preview" tugmasi
@reply_router.message(PostCreation.configuring_post, F.text == "👁️‍🗨️ Preview")
async def preview_post_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    post_data, buttons_matrix = data.get("post_data", {}), data.get("buttons_matrix", [])
    disable_preview = data.get("disable_web_page_preview", False)
    if not post_data: return await message.answer("Xatolik: Post topilmadi.")

    await message.answer("Postning oldindan ko'rinishi:")

    # "buttons_matrix" dan o'qiymiz
    keyboard = generate_preview_keyboard(buttons_matrix)
    content_type, chat_id = post_data.get('content_type'), message.chat.id
    try:
        if content_type == 'album':
            media_group = MediaGroupBuilder(caption=post_data.get("caption"))
            for file in post_data.get('files', []):
                if file['type'] == 'photo': media_group.add_photo(file['file_id'])
                elif file['type'] == 'video': media_group.add_video(file['file_id'])
            await message.bot.send_media_group(chat_id=chat_id, media=media_group.build())
            if keyboard: await message.answer("Tugmalar:", reply_markup=keyboard)
        else:
            file_id, caption, text = post_data.get("file_id"), post_data.get("caption"), post_data.get("text")
            if content_type == 'text':
                await message.bot.send_message(chat_id, text, reply_markup=keyboard, disable_web_page_preview=disable_preview)
            elif content_type == 'photo':
                await message.bot.send_photo(chat_id, file_id, caption=caption, reply_markup=keyboard)
            elif content_type == 'video':
                await message.bot.send_video(chat_id, file_id, caption=caption, reply_markup=keyboard)
            elif content_type == 'audio':
                 await message.bot.send_audio(chat_id, file_id, caption=caption, reply_markup=keyboard)
            elif content_type == 'document':
                 await message.bot.send_document(chat_id, file_id, caption=caption, reply_markup=keyboard)
    except Exception as e:
        logging.error(f"Previewda xatolik: {e}")
        await message.answer("Oldindan ko'rishda xatolik.")

# "❌ Cancel" tugmasi
@reply_router.message(PostCreation.configuring_post, F.text == "❌ Cancel")
async def cancel_post_creation_handler(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Post yaratish bekor qilindi.", reply_markup=get_main_menu())

# "✅ Done" tugmasi
@reply_router.message(PostCreation.configuring_post, F.text == "✅ Done")
async def done_post_creation(message: types.Message, state: FSMContext):
    data = await state.get_data()
    post_data = data.get("post_data")
    buttons_matrix = data.get("buttons_matrix", [])
    if not post_data:
        return await message.answer("Xatolik: Saqlash uchun post topilmadi.")

    try:
        post_code = add_post_to_db(message.from_user.id, post_data, buttons_matrix)
    except Exception as e:
        logging.error(f"DBga saqlashda xatolik: {e}")
        return await message.answer("Postni saqlashda xatolik yuz berdi.")

    await state.clear()
    bot_info = await message.bot.get_me()
    await message.answer(
        f"☑️ Post saqlandi. Noyob kodingiz: `{post_code}`\n\n"
        f"Endi istalgan chatda `@{bot_info.username} {post_code}` deb yozing!",
        reply_markup=get_main_menu(), parse_mode="Markdown"
            )
