import os
import logging
from flask import Flask, request, jsonify
from aiogram import Bot
from bot import dp, setup_bot
from aiogram.webhook.aiohttp_server import SimpleRequestHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "default_secret_token")

async def on_startup(bot: Bot):
    await setup_bot()
    await bot.set_webhook(
        f"https://{os.getenv('RENDER_SERVICE_NAME')}.onrender.com/webhook",
        secret_token=WEBHOOK_SECRET,
        drop_pending_updates=True
    )
    logger.info("Webhook o'rnatildi")

@app.route('/')
def home():
    return "Bot serveri ishlamoqda! /set_webhook orqali webhookni o'rnating."

@app.route('/set_webhook')
async def set_webhook_route():
    try:
        bot = Bot(token=os.getenv("BOT_TOKEN"))
        await on_startup(bot)
        return "Webhook muvaffaqiyatli o'rnatildi!"
    except Exception as e:
        logger.error(f"Webhook o'rnatishda xatolik: {e}")
        return f"Xatolik: {str(e)}", 500

@app.route('/webhook', methods=['POST'])
async def webhook():
    if request.headers.get('X-Telegram-Bot-Api-Secret-Token') != WEBHOOK_SECRET:
        return jsonify({"status": "forbidden"}), 403
    
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    update = request.json
    await dp.feed_webhook_update(bot, update)
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=True)
