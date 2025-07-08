import asyncio
import logging
from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.media_group import MediaGroupBuilder
from typing import List, Dict

from states.post_states import PostCreation
from keyboards.reply import get_post_settings_kb
from keyboards.inline import generate_post_keyboard

post_creation_router = Router()

media_groups: Dict[str, List[Message]] = {}

@post_creation_router.message(PostCreation.waiting_for_content)
async def universal_content_handler(message: Message, state: FSMContext):
    # 1. Agar xabar Rasm/Video guruhi bo'lsa
    if message.media_group_id and message.content_type in ('photo', 'video'):
        if message.media_group_id not in media_groups:
            media_groups[message.media_group_id] = [message]
            await asyncio.sleep(0.7)
            album = media_groups.pop(message.media_group_id, None)
            if not album: return # Agar boshqa handler ishlab bo'lgan bo'lsa

            await state.clear()
            await state.set_state(PostCreation.configuring_post)

            post_data = {'content_type': 'album', 'caption': next((m.caption for m in album if m.caption), None)}
            files = []
            for msg in album:
                if msg.photo: files.append({'type': 'photo', 'file_id': msg.photo[-1].file_id})
                elif msg.video: files.append({'type': 'video', 'file_id': msg.video.file_id})
            post_data['files'] = files

            media_group = MediaGroupBuilder(caption=post_data['caption'])
            for file in post_data['files']:
                if file['type'] == 'photo': media_group.add_photo(file['file_id'])
                elif file['type'] == 'video': media_group.add_video(file['file_id'])

            await message.bot.send_media_group(chat_id=message.chat.id, media=media_group.build())
            await message.answer("Albom qabul qilindi. Unga tugma qo'shib bo'lmaydi.", reply_markup=get_post_settings_kb())
            await state.update_data(post_data=post_data)
        else:
            media_groups[message.media_group_id].append(message)
        return

    # 2. Agar yakka xabar bo'lsa
    elif not message.media_group_id:
        if message.content_type in ('text', 'photo', 'video', 'audio', 'document'):
            await state.clear()
            await state.set_state(PostCreation.configuring_post)

            post_data = {'content_type': message.content_type, 'chat_id': message.chat.id}
            keyboard = generate_post_keyboard() if message.content_type in ('text', 'photo', 'video') else None

            sent_message = None
            if message.photo:
                post_data.update({'file_id': message.photo[-1].file_id, 'caption': message.caption})
                sent_message = await message.bot.send_photo(message.chat.id, post_data['file_id'], caption=post_data['caption'], reply_markup=keyboard)
            elif message.video:
                post_data.update({'file_id': message.video.file_id, 'caption': message.caption})
                sent_message = await message.bot.send_video(message.chat.id, post_data['file_id'], caption=post_data['caption'], reply_markup=keyboard)
            elif message.audio:
                post_data.update({'file_id': message.audio.file_id, 'caption': message.caption})
                sent_message = await message.bot.send_audio(message.chat.id, post_data['file_id'], caption=post_data['caption'])
            elif message.document:
                post_data.update({'file_id': message.document.file_id, 'caption': message.caption})
                sent_message = await message.bot.send_document(message.chat.id, post_data['file_id'], caption=post_data['caption'])
            elif message.text:
                post_data['text'] = message.html_text
                sent_message = await message.bot.send_message(message.chat.id, post_data['text'], reply_markup=keyboard)

            if sent_message:
                post_data['message_id'] = sent_message.message_id
                await state.update_data(post_data=post_data)
                msg_text = "Fayl qabul qilindi. Bunga tugma qo'shib bo'lmaydi." if not keyboard else "Post qabul qilindi."
                await message.answer(msg_text, reply_markup=get_post_settings_kb())
            return

    # 3. Qolgan barcha holatlar (stiker, lokatsiya, audio/dokument guruhlari)
    await message.answer("❌ Noto'g'ri format yoki amal!")
