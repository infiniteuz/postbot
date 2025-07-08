import re
import logging
from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton

from states.post_states import PostCreation
from keyboards.reply import get_post_settings_kb, get_cancel_kb
from keyboards.inline import generate_post_keyboard

button_router = Router()
URL_PATTERN = re.compile(r"^(https?://)?([\w-]{1,32}\.[\w-]{1,32})[^\s@]*$")

# 1-QISM: YANGI TUGMA YARATISH YOKI ESKISINI TAHRIRLASH

@button_router.callback_query(PostCreation.configuring_post, F.data.startswith("add:"))
@button_router.message(PostCreation.configuring_post, F.text == "✏️ Tahrirlash")
async def start_button_creation_or_edit(event: types.Union[types.CallbackQuery, types.Message], state: FSMContext):
    if isinstance(event, types.CallbackQuery):
        coords = event.data.split(':')[1:]
        await state.update_data(target_button_coords=(int(coords[0]), int(coords[1])))
        await state.update_data(is_button_editing=False)
        message = event.message
        try: await message.delete()
        except: pass
    else:
        data = await state.get_data()
        if not data.get("editing_button_coords"):
            return await event.answer("Avval tahrirlash uchun inline tugmani bosing.")
        await state.update_data(is_button_editing=True)
        message = event

    await state.set_state(PostCreation.waiting_for_button_text)
    await message.answer("Tugma uchun YANGI matnni yuboring:", reply_markup=get_cancel_kb())
    if isinstance(event, types.CallbackQuery): await event.answer()

@button_router.message(PostCreation.waiting_for_button_text, F.text)
async def ask_for_button_url(message: types.Message, state: FSMContext):
    await state.update_data(button_text=message.text)
    await message.answer("Ajoyib! Endi YANGI URL manzilini yuboring:", reply_markup=get_cancel_kb())
    await state.set_state(PostCreation.waiting_for_button_url)

@button_router.message(PostCreation.waiting_for_button_url, F.text)
async def add_or_edit_button(message: types.Message, state: FSMContext):
    user_url = message.text
    if not user_url.startswith(('http://', 'https://')): user_url = 'https://' + user_url
    if not URL_PATTERN.match(user_url): return await message.answer("❌ Noto'g'ri URL!")

    data = await state.get_data()
    button_text = data.get("button_text")
    buttons_matrix = data.get("buttons_matrix", [])

    if data.get("is_button_editing"):
        target_row, target_col = data.get("editing_button_coords")
        status_text = "Tugma tahrirlandi ✅"
    else:
        target_row, target_col = data.get("target_button_coords")
        status_text = "Tugma qo'shildi ✅"

    while len(buttons_matrix) <= target_row: buttons_matrix.append([])
    while len(buttons_matrix[target_row]) <= target_col: buttons_matrix[target_row].append(None)
    buttons_matrix[target_row][target_col] = {'text': button_text, 'url': user_url}

    # SXEMA BO'YICHA QAYTA QURISH
    if not data.get("is_button_editing"):
        # Hamma ➕ larni tozalaymiz
        temp_matrix = [[btn for btn in row if btn and not btn.get('is_placeholder')] for row in buttons_matrix if any(btn and not btn.get('is_placeholder') for btn in row)]

        # Yangi ➕ larni qo'yamiz
        final_matrix = []
        for r_idx, row in enumerate(temp_matrix):
            new_row = list(row)
            new_row.append({'is_placeholder': True})
            final_matrix.append(new_row)

        # Pastki qatorni qo'shish
        if not final_matrix or any(btn and not btn.get('is_placeholder') for btn in final_matrix[-1]):
             final_matrix.append([{'is_placeholder': True}])
        buttons_matrix = final_matrix

    await state.update_data(buttons_matrix=buttons_matrix, is_button_editing=False, editing_button_coords=None, target_button_coords=None)
    await state.set_state(PostCreation.configuring_post)
    await message.answer(status_text, reply_markup=get_post_settings_kb())

    new_keyboard = generate_post_keyboard(buttons_matrix)
    post_data = data.get("post_data", {})
    if not post_data: return

    try: await message.bot.delete_message(post_data.get("chat_id"), post_data.get("message_id"))
    except: pass

    content_type = post_data.get('content_type')
    chat_id = post_data.get("chat_id")
    try:
        if content_type == 'photo':
            sent_message = await message.bot.send_photo(chat_id, post_data.get("file_id"), caption=post_data.get("caption"), reply_markup=new_keyboard)
        else:
            sent_message = await message.bot.send_message(chat_id, text=post_data.get("text"), reply_markup=new_keyboard)
        post_data['message_id'] = sent_message.message_id
        await state.update_data(post_data=post_data)
    except Exception as e:
        logging.error(f"Postni qayta yuborishda xatolik: {e}")

# 2-QISM: YARATILGAN TUGMANI BOSHQARISH

@button_router.callback_query(PostCreation.configuring_post, F.data.startswith("edit_btn:"))
async def select_button_for_action(callback: types.CallbackQuery, state: FSMContext):
    coords = callback.data.split(':')[1:]
    await state.update_data(editing_button_coords=(int(coords[0]), int(coords[1])))

    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="🗑️ O'chirish"), KeyboardButton(text="✏️ Tahrirlash"), KeyboardButton(text="◀️ Ortga"))

    try: await callback.message.edit_reply_markup(reply_markup=None)
    except: pass

    await callback.message.answer("Ushbu tugma bilan nima qilmoqchisiz?", reply_markup=builder.as_markup(resize_keyboard=True))
    await callback.answer()

@button_router.message(PostCreation.configuring_post, F.text == "◀️ Ortga")
async def back_from_edit_button(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(editing_button_coords=None)

    await message.answer("Asosiy sozlash menyusiga qaytildi.", reply_markup=get_post_settings_kb())

    buttons_matrix = data.get("buttons_matrix", [])
    new_keyboard = generate_post_keyboard(buttons_matrix)
    post_data = data.get("post_data", {})
    try:
        await message.bot.edit_message_reply_markup(chat_id=post_data.get("chat_id"), message_id=post_data.get("message_id"), reply_markup=new_keyboard)
    except: pass

@button_router.message(PostCreation.configuring_post, F.text == "🗑️ O'chirish")
async def delete_button(message: types.Message, state: FSMContext):
    data = await state.get_data()
    coords = data.get("editing_button_coords")
    if not coords: return

    target_row, target_col = coords
    buttons_matrix = data.get("buttons_matrix", [])

    if len(buttons_matrix) > target_row and len(buttons_matrix[target_row]) > target_col:
        buttons_matrix[target_row][target_col] = None

    await state.update_data(buttons_matrix=buttons_matrix, editing_button_coords=None)
    await message.answer("Tugma o'chirildi ✅", reply_markup=get_post_settings_kb())

    new_keyboard = generate_post_keyboard(buttons_matrix)
    post_data = data.get("post_data", {})
    try:
        await message.bot.edit_message_reply_markup(
            chat_id=post_data.get("chat_id"), message_id=post_data.get("message_id"),
            reply_markup=new_keyboard
        )
    except Exception as e: logging.error(f"Postni tahrirlashda xatolik: {e}")
