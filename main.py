import asyncio
import json
import logging
import os
import time

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from fastapi import FastAPI
import uvicorn

# =======================
# CONFIG
# =======================
BOT_TOKEN = "8618077281:AAHCUmkUf9g6ZG56QxSLLl5F27of4eLR_YY"
GROUP_ID = -1003874749853       # Adminlar guruhi
ADMIN_ID = 8223476380           # Sizning admin ID
MESSAGES_DB_FILE = "messages_db.json"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
last_message_time = {}  # Spam filter uchun

# =======================
# FSM State
# =======================
class TrustBox(StatesGroup):
    waiting_for_message = State()

# =======================
# DB funksiyalari
# =======================
def load_messages_db():
    if os.path.exists(MESSAGES_DB_FILE):
        try:
            with open(MESSAGES_DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_messages_db(db):
    with open(MESSAGES_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def add_message_link(msg_id, user_id):
    db = load_messages_db()
    db[str(msg_id)] = user_id
    save_messages_db(db)

def get_user_id(msg_id):
    db = load_messages_db()
    return db.get(str(msg_id))

# =======================
# Main menu
# =======================
def main_menu():
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="🏫 Maktabimiz haqida")],
            [
                types.KeyboardButton(text="📝 Ariza topshirish"),
                types.KeyboardButton(text="📮 Ishonch qutisi")
            ],
            [types.KeyboardButton(text="👨‍💻 Adminlar bilan bogʻlanish")]
        ],
        resize_keyboard=True
    )
    return keyboard

# =======================
# /start
# =======================
@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await state.set_state(TrustBox.waiting_for_message)
    await message.answer(
        f"✨ Assalomu alaykum: {message.from_user.full_name}\n"
        "🔰 Botimizga xush kelibsiz\n"
        "🤖 Quyidagi tugmalardan foydalaning 👇",
        reply_markup=main_menu()
    )

# =======================
# Menu handler
# =======================
@dp.message(TrustBox.waiting_for_message)
async def menu_handler(message: types.Message, state: FSMContext):
    text = message.text

    if text == "🏫 Maktabimiz haqida":
        await message.answer(
            "NAMANGAN SHAHAR 1-SON IXTISOSLASHTIRILGAN MAKTAB INTERNATI – KELAJAK TALABALARI MASKANI!\n\n2026-2027 o‘quv yili uchun \n\n🌟 Aniq va tabiiy fanlarga ixtisoslashgan maktab-internat 4- va 6-sinf bitiruvchilarini imtihonga taklif etadi!\n\n🎯 Maktab-internat afzalliklari:\n• Matematika, fizika, kimyo, biologiya va ingliz tili fanlari chuqurlashtirib o‘qitiladi\n• Zamonaviy jihozlangan fan laboratoriyalari\n• Malakali va fidoyi o‘qituvchilar\n• Darsdan tashqari to‘garaklar\n• Bepul yotoqxona\n• 5 mahal bepul ovqat\n• Muddatdan avval talabalik imkoniyati!\n\n🏆 OTMga kirish ko‘rsatkichlari:\n2023-yil bitiruvchilari: 100%\n2024-yil bitiruvchilari: 97%\n2025-yil bitiruvchilari: 100%\n\n🏫 Manzil: Namangan sh., Dashtbog‘ MFY, Sanoat ko‘chasi, 101-uy",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [types.InlineKeyboardButton(text="🔰 Batafsil", url="https://t.me/pm_nam_imi")]
                ]
            )
        )

    elif text == "📝 Ariza topshirish":
        await message.answer(
            "📝 Namangan shahar 1-son ixtisoslashtirilgan maktab internatiga ariza topshirish onlayn tarzda amalga oshiriladi.\n\n📌 Ariza topshirish 2026-yil 1-20 iyun kunlari.\n\nAriza berish👇",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [types.InlineKeyboardButton(text="📝 Ariza berish", url="https://ariza.piima.uz")]
                ]
            )
        )

    elif text == "📮 Ishonch qutisi":
        await message.answer(
            "📩 Habaringizni yuboring, adminlar siz bilan bogʻlanadi.\n"
            "Bilib qoʻying, shaxsingiz sir saqlanadi 🤐",
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.set_state(TrustBox.waiting_for_message)

    elif text == "👨‍💻 Adminlar bilan bogʻlanish":
        await message.answer(
            "ADMINGA HABAR BOʻLIMI\n\nBu bo‘lim orqali savollarga javob olishingiz mumkin👇",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [types.InlineKeyboardButton(text="☎️ Murojaat qilish", url="https://t.me/axe_adm_bot")]
                ]
            )
        )

# =======================
# Ishonch qutisi xabari → guruhga anonim
# =======================
@dp.message(TrustBox.waiting_for_message)
async def send_to_group(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    now = time.time()

    # Spam filter 30 soniya
    if user_id in last_message_time and now - last_message_time[user_id] < 30:
        await message.answer("❌ Iltimos 30 soniya kutib keyin yozing")
        return
    last_message_time[user_id] = now

    # Guruhga yuborish
    sent = await bot.send_message(GROUP_ID, f"📮 Ishonch qutisi\n\n💬 {message.text}")
    add_message_link(sent.message_id, user_id)

    # Foydalanuvchiga tasdiq
    await message.answer("✅ Xabaringiz yuborildi, adminlar javob beradi", reply_markup=main_menu())
    await state.clear()

# =======================
# Admin reply → foydalanuvchiga
# =======================
@dp.message(F.chat.id == GROUP_ID, F.reply_to_message)
async def admin_reply(message: types.Message):
    replied_id = message.reply_to_message.message_id
    user_id = get_user_id(replied_id)
    if user_id:
        await bot.send_message(user_id, f"📩 Admin javobi:\n{message.text}")
        await message.reply("✅ Foydalanuvchiga yuborildi")
    else:
        await message.reply("❌ Foydalanuvchi topilmadi")

# =======================
# Statistika (faqat admin)
# =======================
@dp.message(Command("stat"))
async def stats(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    db = load_messages_db()
    await message.answer(f"📊 Murojaatlar soni: {len(db)}")

# =======================
# FASTAPI + polling
# =======================
app = FastAPI()

@app.on_event("startup")
async def on_startup():
    await bot.delete_webhook(drop_pending_updates=True)
    asyncio.create_task(dp.start_polling(bot, skip_updates=True))

@app.get("/")
def home():
    return {"status": "Bot ishlayapti"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
