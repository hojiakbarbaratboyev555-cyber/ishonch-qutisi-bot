𝗛𝗼𝗷𝗶𝗮𝗸𝗯𝗮𝗿𝗶𝘆 🇸🇦:
import asyncio
import logging
import json
import os
import time
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardRemove
)
from fastapi import FastAPI
import uvicorn

BOT_TOKEN = "8618077281:AAGe32ooyqGZrPV1o3uu2XSt_Rm9TTL56ZA"
GROUP_ID = -4827270328
ADMIN_ID = 8223476380

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

MESSAGES_DB_FILE = "messages_db.json"
last_message_time = {}

class TrustBox(StatesGroup):
    waiting_for_message = State()

def load_messages_db():
    if os.path.exists(MESSAGES_DB_FILE):
        try:
            with open(MESSAGES_DB_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_messages_db(db):
    with open(MESSAGES_DB_FILE, "w") as f:
        json.dump(db, f)

def add_message_link(msg_id, user_id):
    db = load_messages_db()
    db[str(msg_id)] = user_id
    save_messages_db(db)

def get_user_id(msg_id):
    db = load_messages_db()
    return db.get(str(msg_id))

@dp.message(Command("start"))
async def start(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📮 𝗜𝗦𝗛𝗢𝗡𝗖𝗛 𝗤𝗨𝗧𝗜𝗦𝗜")]],
        resize_keyboard=True
    )

    inline = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="𝗠𝗔𝗞𝗧𝗔𝗕 𝗬𝗔𝗡𝗚𝗜𝗟𝗜𝗞𝗟𝗔𝗥𝗜 🗞️", url="https://t.me/pm_nam_imi")],
            [InlineKeyboardButton(text="𝗖𝗥𝗘𝗔𝗧𝗢𝗥𝗚𝗔 𝗠𝗨𝗥𝗢𝗝𝗔𝗔𝗧 👨‍💻", url="https://t.me/recipient_robot")]
        ]
    )

    await message.answer(
        "Bu bot orqali siz ariza yoki takliflaringizni yuborishingiz mumkin.\nAdminlar sizga javob yuborishadi.\n\nSizning shaxsingiz sir saqlanadi🤐\n\nPastadi 𝗜𝘀𝗵𝗼𝗻𝗰𝗵 𝗾𝘂𝘁𝗶𝘀𝗶 tugmasi ustiga bosing",
        reply_markup=keyboard
    )

    await message.answer("Qo‘shimcha ma'lumotlar uchun:", reply_markup=inline)

@dp.message(F.text == "📮 𝗜𝗦𝗛𝗢𝗡𝗖𝗛 𝗤𝗨𝗧𝗜𝗦𝗜")
async def trust_box(message: types.Message, state: FSMContext):
    await message.answer(
        "Savol va murojaatingizni yuboring",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(TrustBox.waiting_for_message)

@dp.message(TrustBox.waiting_for_message, F.text)
async def send_text(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    now = time.time()

    if user_id in last_message_time:
        if now - last_message_time[user_id] < 30:
            await message.answer("❌ 30 soniya kutib keyin yozing")
            return

    last_message_time[user_id] = now

    text = f"📮 𝗜𝘀𝗵𝗼𝗻𝗰𝗵 𝗾𝘂𝘁𝗶𝘀𝗶\n\n💬 {message.text}"

    sent = await bot.send_message(GROUP_ID, text)
    add_message_link(sent.message_id, user_id)

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📮 𝗜𝗦𝗛𝗢𝗡𝗖𝗛 𝗤𝗨𝗧𝗜𝗦𝗜")]],
        resize_keyboard=True
    )

    await message.answer("✅ Xabaringiz yuborildi. Tez orada javob xati keladi. Sizdan kutishingizni iltimos qilamiz", reply_markup=keyboard)
    await state.clear()

@dp.message(F.chat.id == GROUP_ID, F.reply_to_message)
async def admin_reply(message: types.Message):
    replied = message.reply_to_message.message_id
    user_id = get_user_id(replied)

    if user_id:
        await bot.send_message(
            user_id,
            f"{message.text}"
        )
        await message.reply("✅ Foydalanuvchiga yuborildi")
    else:
        await message.reply("❌ Foydalanuvchi topilmadi")

@dp.message(Command("stat"))
async def stats(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    db = load_messages_db()
    await message.answer(f"📊 Statistika\n\n📩 Murojaatlar soni: {len(db)}")

# ===============================
# FASTAPI + BOT BIRGA
# ===============================
app = FastAPI()

@app.on_event("startup")
async def on_startup():
    # Botni background task sifatida ishga tushiramiz
    asyncio.create_task(dp.start_polling(bot))

@app.get("/")
def home():
    return {"status": "Bot ishlayapti"}

if name == "main":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
