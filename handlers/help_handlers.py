from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

help_router = Router()

@help_router.message(Command("help"))
async def help_command(message: Message):
    help_text = (
        "🤖 Botdan foydalanish qo'llanmasi:\n\n"
        "✍️ Post yaratish - Yangi post yaratish uchun\n"
        "📝 Post tahrirlash - Avval yaratilgan postni tahrirlash\n"
        "⚙️ Til sozlamalari - Bot tilini o'zgartirish\n\n"
        "Admin bilan bog'lanish: @ibrakhimov_gpt"
    )
    await message.answer(help_text)
