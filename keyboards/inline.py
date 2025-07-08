from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Dict, Optional

def generate_post_keyboard(buttons_matrix: Optional[List[List[Optional[Dict]]]] = None):
    # ... (avvalgi kod) ...
    pass

def generate_preview_keyboard(buttons_matrix: Optional[List[List[Optional[Dict]]]] = None):
    # ... (avvalgi kod) ...
    pass

def get_admin_panel_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📝 Start xabarini tahrirlash", callback_data="admin_startmsg"))
    builder.row(InlineKeyboardButton(text="🖼️ Watermark tahrirlash", callback_data="admin_watermark"))
    builder.row(InlineKeyboardButton(text="🔘 Watermark yoqish/o'chirish", callback_data="admin_toggle_wm"))
    return builder.as_markup()
