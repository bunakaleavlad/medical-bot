import os
import asyncio
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes

# ===== 1. СПОЧАТКУ FLASK =====
app = Flask(__name__)

# ===== 2. ТОКЕН =====
TOKEN = os.environ.get('TOKEN')
if not TOKEN:
    raise ValueError("TOKEN not found in environment")

VERCEL_URL = "https://medical-bot-three.vercel.app"
CHANNEL_URL = "https://t.me/propofolcoffe"
BASE_URL = f"{VERCEL_URL}/webapps"

# ===== 3. ВІДКЛАДЕНА ІНІЦІАЛІЗАЦІЯ БОТА =====
_bot_instance = None
_bot_initialized = False

async def init_bot():
    global _bot_instance, _bot_initialized
    if not _bot_initialized:
        await _bot_instance.initialize()
        _bot_initialized = True

def get_bot():
    global _bot_instance
    if _bot_instance is None:
        _bot_instance = Application.builder().token(TOKEN).build()
        
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

# ===== 4. РОУТИ =====
@app.route('/')
def home():
    return '✅ MediCalc Bot is running!'

@app.route('/webhook', methods=['POST'])
def webhook():
    bot = get_bot()
    data = request.get_json(force=True)
    update = Update.de_json(data, bot.bot)
    
    async def process():
        if not _bot_initialized:
            await bot.initialize()
        await bot.process_update(update)
    
    asyncio.run(process())
    
    return jsonify({"status": "ok"})
