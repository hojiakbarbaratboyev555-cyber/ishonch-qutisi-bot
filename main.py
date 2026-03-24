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
BOT_TOKEN = "TOKENINGNI_QO'Y"
GROUP_ID = -1003874749853
ADMIN_ID = 8223476380
MESSAGES_DB_FILE = "messages_db.json"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()  # ✅ TO‘G‘RI

last_message_time = {}

# =======================
# FSM
# =======================
class TrustBox(StatesGroup):
    waiting_for_message = State()

# =======================
# DB
# =======================
def load_db():
    if os.path.exists(MESSAGES_DB_FILE):
        with open(MESSAGES_DB_FILE, "r") as f:
            return json.load(f)
    return {}

def save_db(data):
    with open(MESSAGES_DB_FILE, "w") as f:
        json.dump(data, f)

def add_link(msg_id, user_id):
    db = load_db()
    db[str(msg_id)] = user_id
    save_db(db)

def get_user(msg_id):
    return load_db().get(str(msg_id))

# =======================
# MENU
# =======================
def main_menu():
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="📮 Ishonch qutisi")]
        ],
        resize_keyboard=True
    )

# =======================
# START
# =======================
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "Assalomu alaykum 👋\nKerakli bo‘limni tanlang",
        reply_markup=main_menu()
    )

# =======================
# MENU HANDLER
# =======================
@dp.message(F.text == "📮 Ishonch qutisi")
async def trust_start(message: types.Message, state: FSMContext):
    await message.answer(
        "📩 Xabar yuboring (anonim)",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(TrustBox.waiting_for_message)

# =======================
# XABAR QABUL QILISH
# =======================
@dp.message(TrustBox.waiting_for_message)
async def send_to_group(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    now = time.time()

    # SPAM FILTER
    if user_id in last_message_time and now - last_message_time[user_id] < 30:
        await message.answer("❌ 30 soniya kuting")
        return

    last_message_time[user_id] = now

    # GURUHGA YUBORISH
    sent = await bot.send_message(
        GROUP_ID,
        f"📮 Ishonch qutisi\n\n💬 {message.text}"
    )

    add_link(sent.message_id, user_id)

    await message.answer(
        "✅ Yuborildi",
        reply_markup=main_menu()
    )
    await state.clear()

# =======================
# ADMIN REPLY
# =======================
@dp.message(F.chat.id == GROUP_ID, F.reply_to_message)
async def admin_reply(message: types.Message):
    replied_id = message.reply_to_message.message_id
    user_id = get_user(replied_id)

    if user_id:
        await bot.send_message(
            user_id,
            f"📩 Admin javobi:\n{message.text}"
        )
        await message.reply("✅ Yuborildi")
    else:
        await message.reply("❌ Topilmadi")

# =======================
# STAT
# =======================
@dp.message(Command("stat"))
async def stat(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    db = load_db()
    await message.answer(f"📊 Jami: {len(db)}")

# =======================
# FASTAPI
# =======================
app = FastAPI()

@app.on_event("startup")
async def startup():
    await bot.delete_webhook(drop_pending_updates=True)
    asyncio.create_task(dp.start_polling(bot))

@app.get("/")
def home():
    return {"status": "ok"}

# =======================
# RUN
# =======================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
