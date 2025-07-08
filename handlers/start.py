from aiogram import F, Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from keyboards.reply import get_main_menu, get_cancel_kb
from states.post_states import PostCreation

start_router = Router()

@start_router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    start_text = (f"Xush kelibsiz, <b>{message.from_user.full_name}</b>! 👋\n\n"
                  "Ushbu botdan foydalanib, siz ajoyib postlar yaratishingiz mumkin.")
    await message.answer(start_text, reply_markup=get_main_menu())

@start_router.message(F.text == "✍️ Post yaratish")
async def start_post_creation(message: types.Message, state: FSMContext):
    await message.answer("O'z postingiz mazmunini yuboring! Faqat matn, rasm yoki video qabul qilinadi.",
                         reply_markup=get_cancel_kb())
    await state.set_state(PostCreation.waiting_for_content)

@start_router.message(F.text == "❌ Bekor qilish")
async def cancel_action(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None: return
    await state.clear()
    await message.answer("Amal bekor qilindi.", reply_markup=get_main_menu())
