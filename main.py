import os
import asyncio
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes

# ===== 1. FLASK =====
app = Flask(__name__)

# ===== 2. ТОКЕН =====
TOKEN = os.environ.get('TOKEN')
if not TOKEN:
    raise ValueError("TOKEN not found in environment")

# ===== 3. URL =====
RENDER_URL = os.environ.get('RENDER_EXTERNAL_URL', 'http://localhost:5000')
if 'localhost' in RENDER_URL:
    RENDER_URL = 'http://localhost:5000'

CHANNEL_URL = "https://t.me/propofolcoffe"
BASE_URL = f"{RENDER_URL}/webapps"

# ===== 4. БОТ (ПРАВИЛЬНЕ НАЛАШТУВАННЯ ДЛЯ ВЕБХУКІВ) =====
_bot_instance = None

def get_bot():
    global _bot_instance
    if _bot_instance is None:
        # ВАЖЛИВО: .updater(None) — штатне відключення polling для вебхуків
        _bot_instance = Application.builder().token(TOKEN).updater(None).build()
        
        async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
            keyboard = [
                [InlineKeyboardButton(
                    "🔬 Електроліти (Na⁺, K⁺, Ca²⁺, Mg²⁺)",
                    web_app=WebAppInfo(url=f"{BASE_URL}/electrolytes/")
                )],
                [InlineKeyboardButton(
                    "🫁 КОС (pH, BE, гази крові)",
                    web_app=WebAppInfo(url=f"{BASE_URL}/acidbase/")
                )],
                [InlineKeyboardButton(
                    "💊 Інфузії препаратів",
                    web_app=WebAppInfo(url=f"{BASE_URL}/infusions/")
                )],
                [InlineKeyboardButton(
                    "📊 Шкали (APACHE II, SOFA, RASS)",
                    web_app=WebAppInfo(url=f"{BASE_URL}/scales/")
                )],
                [InlineKeyboardButton(
                    "📢 Наш Telegram канал",
                    url=CHANNEL_URL
                )],
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "🧑‍⚕️ **MediCalc — Медичний Калькулятор**\n\n"
                "Оберіть потрібний розділ.\n"
                "Калькулятор відкриється прямо в Telegram.\n\n"
                "📢 Підпишіться на наш канал — там корисні матеріали!",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        
        _bot_instance.add_handler(CommandHandler("start", start))
    
    return _bot_instance

# ===== 5. ІНІЦІАЛІЗАЦІЯ ПРИ СТАРТІ =====
@app.before_request
def init_on_first_request():
    get_bot()

# ===== 6. РОУТИ =====
@app.route('/')
def home():
    return '✅ MediCalc Bot is running on Render!'

@app.route('/ping', methods=['GET'])
def ping():
    return 'pong'

@app.route('/webhook', methods=['POST'])
def webhook():
    bot = get_bot()
    data = request.get_json(force=True)
    
    async def process():
        await bot.initialize()
        update = Update.de_json(data, bot.bot)
        await bot.process_update(update)
    
    asyncio.run(process())
    
    return jsonify({"status": "ok"})

# ===== 7. ЛОКАЛЬНИЙ ЗАПУСК =====
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
