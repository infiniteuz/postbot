import logging
from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from keyboards.inline import get_admin_panel_kb

admin_router = Router()
ADMIN_ID = int(os.getenv("ADMIN_ID", 5720724311))

# Admin buyrug'i
@admin_router.message(Command("admin"))
async def admin_command(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Siz admin emassiz!")
        return
        
    await message.answer("Admin paneli:", reply_markup=get_admin_panel_kb())

# Admin paneli tugmalari
@admin_router.callback_query(F.data.startswith("admin_"))
async def admin_panel_handler(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Siz admin emassiz!", show_alert=True)
        return
        
    action = callback.data.split("_")[1]
    
    if action == "startmsg":
        await callback.message.answer("Yangi start xabarini yuboring:")
        # FSM holatini o'rnatish kerak
    elif action == "watermark":
        await callback.message.answer("Watermark sozlamalari:")
        # Watermark sozlamalari
    elif action == "toggle_wm":
        # Watermark yoqish/o'chirish logikasi
        await callback.answer("Watermark holati o'zgartirildi!")
    
    await callback.answer()
