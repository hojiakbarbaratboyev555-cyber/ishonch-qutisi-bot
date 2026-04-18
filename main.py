import asyncio
import logging
import json
import os
from threading import Thread

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from flask import Flask

# ==========================================
# 1. SOZLAMALAR VA LINKLAR
# ==========================================
BOT_TOKEN = "8760367023:AAFkPdKHuT9Vau8kL6BOwXyoD8GJv7iB94g"
GROUP_ID = -1003874749853
MESSAGES_DB_FILE = "messages_db.json"

# Rasmlar linklari
SCHOOL_LOGO_URL = "https://r.jina.ai/i/06c2890526014e049195a63973942004"
TRUST_BOX_URL = "https://r.jina.ai/i/0126569199324700994f326196232230"
ADMIN_PHOTO_URL = "https://r.jina.ai/i/012111516244460023a131a424221151"
APPLICATION_URL = "https://r.jina.ai/i/0222115622344700914f326196232230"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

class TrustBox(StatesGroup):
    waiting_for_message = State()

# ==========================================
# 2. MA'LUMOTLAR BAZASI
# ==========================================
def load_messages():
    if os.path.exists(MESSAGES_DB_FILE):
        try:
            with open(MESSAGES_DB_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}

def save_messages(data):
    with open(MESSAGES_DB_FILE, "w") as f: json.dump(data, f, indent=4)

# ==========================================
# 3. KLAVIATURA
# ==========================================
def main_menu():
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="🏫 Maktabimiz haqida")],
            [types.KeyboardButton(text="📝 Ariza topshirish"), types.KeyboardButton(text="📮 Ishonch qutisi")],
            [types.KeyboardButton(text="👨‍💻 Adminlar bilan bogʻlanish")]
        ],
        resize_keyboard=True
    )

# ==========================================
# 4. HANDLERLAR
# ==========================================
@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(f"✨ Assalomu alaykum: {message.from_user.full_name}\nNamangan shahar 1-IMI botiga xush kelibsiz!", reply_markup=main_menu())

@dp.message(StateFilter(None), F.text.in_({"🏫 Maktabimiz haqida", "📝 Ariza topshirish", "📮 Ishonch qutisi", "👨‍💻 Adminlar bilan bogʻlanish"}))
async def menu_handler(message: types.Message, state: FSMContext):
    if message.text == "🏫 Maktabimiz haqida":
        caption = "🏢 **NAMANGAN SHAHAR 1-SON IMI**\n\n🎯 Aniq va tabiiy fanlar chuqurlashtirib o'qitiladi.\n🏫 Manzil: Namangan sh., Dashtbog‘ MFY, Sanoat ko'chasi, 101-uy"
        await message.answer_photo(photo=SCHOOL_LOGO_URL, caption=caption, parse_mode="Markdown",
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(text="🔰 Kanalimiz", url="https://t.me/pm_nam_imi")]]))

    elif message.text == "📮 Ishonch qutisi":
        caption = "📩 **Ishonch qutisi**\n\n🏫 Maktab maʼmuriyatiga oʻz savollaringizni yuboring.\n👤 Shaxsingiz sir saqlanadi.\n\n📝 **Xabaringizni yozing:**"
        await message.answer_photo(photo=TRUST_BOX_URL, caption=caption, parse_mode="Markdown", reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(TrustBox.waiting_for_message)

    elif message.text == "📝 Ariza topshirish":
        caption = "📝 **Onlayn ariza topshirish**\n\nQabul iyun oyida boshlanishi kutilmoqda.\n\n👇 **Portalga o'tish:**"
        await message.answer_photo(photo=APPLICATION_URL, caption=caption, parse_mode="Markdown",
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(text="📝 Ariza berish", url="https://ariza.piima.uz")]]))

    elif message.text == "👨‍💻 Adminlar bilan bogʻlanish":
        caption = "👨‍💻 **Adminlar bilan bog'lanish**\n\nSavollaringiz bo'lsa, adminlarimizga murojaat qiling.\n\n☎️ **Murojaat uchun:**"
        await message.answer_photo(photo=ADMIN_PHOTO_URL, caption=caption, parse_mode="Markdown",
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(text="☎️ Admin", url="https://t.me/axe_adm_bot")]]))

@dp.message(TrustBox.waiting_for_message)
async def send_anonymous(message: types.Message, state: FSMContext):
    if not message.text:
        await message.answer("⚠️ Iltimos, matn yuboring.")
        return
    sent = await bot.send_message(GROUP_ID, f"📮 #Ishonch_qutisi\n\n💬 {message.text}")
    data = load_messages(); data[str(sent.message_id)] = message.from_user.id; save_messages(data)
    await message.answer("✅ Xabaringiz yuborildi.", reply_markup=main_menu()); await state.clear()

@dp.message(F.chat.id == GROUP_ID, F.reply_to_message)
async def admin_reply(message: types.Message):
    data = load_messages()
    user_id = data.get(str(message.reply_to_message.message_id))
    if user_id:
        try:
            await bot.send_message(user_id, f"📩 **Admin javobi:**\n\n{message.text}", parse_mode="Markdown")
            await message.reply("✅ Yuborildi")
        except: await message.reply("❌ Xato")

# ==========================================
# 5. RENDER UCHUN WEB SERVER (KEEP-ALIVE)
# ==========================================
server = Flask('')

@server.route('/')
def home():
    return "Bot is running!"

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_server)
    t.start()

# ==========================================
# 6. RUN
# ==========================================
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    keep_alive() # Render portini faollashtirish
    asyncio.run(main())
