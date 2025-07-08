import logging
import os
from aiogram import Router, types
from aiogram.types import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineQueryResultPhoto
)
from keyboards.inline import generate_preview_keyboard
from utils.database import get_post_from_db

inline_router = Router()

@inline_router.inline_query()
async def inline_query_handler(query: types.InlineQuery):
    post_code = query.query.strip()
    results = []

    if post_code:
        try:
            post_data = get_post_from_db(post_code)

            if post_data:
                content = post_data.get('post_content', {})
                buttons_list = post_data.get('buttons_list', [])
                keyboard = generate_preview_keyboard(buttons_list)

                content_type = content.get('content_type')

                if content_type == 'text':
                    results.append(
                        InlineQueryResultArticle(
                            id=post_code,
                            title="Matnli post",
                            description=(content.get('text', '')[:60] + "...") if content.get('text') else "Matnsiz post",
                            input_message_content=InputTextMessageContent(
                                message_text=content.get('text', ''),
                                parse_mode="HTML"
                            ),
                            reply_markup=keyboard
                        )
                    )
                elif content_type == 'photo':
                    results.append(
                        InlineQueryResultPhoto(
                            id=post_code,
                            photo_file_id=content.get('file_id'),
                            title="Rasmli post",
                            description=content.get('caption', 'Rasm tavsifisiz')[:50],
                            caption=content.get('caption'),
                            parse_mode="HTML",
                            reply_markup=keyboard
                        )
                    )
                elif content_type == 'video':
                    results.append(
                        InlineQueryResultVideo(
                            id=post_code,
                            video_file_id=content.get('file_id'),
                            title="Video post",
                            description=content.get('caption', 'Video tavsifisiz')[:50],
                            caption=content.get('caption'),
                            parse_mode="HTML",
                            reply_markup=keyboard
                        )
                    )

        except Exception as e:
            logging.error(f"Inline rejimda xatolik: {e}")

    if not results:
        results.append(
            InlineQueryResultArticle(
                id="help_msg",
                title="Postni topish uchun kodni kiriting",
                description="Masalan: aBcD1",
                input_message_content=InputTextMessageContent(
                    message_text="Iltimos, botga qaytib, post yarating va uning noyob kodini oling."
                )
            )
        )

    await query.answer(results, cache_time=0)
