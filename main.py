import asyncio
import logging
import json
import os
import time

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types = (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardRemove
)

BOT_TOKEN = "8397626217:AAGFjDQgLR_cgwCmtiuzYFmdBQ8EaE4Ru2E"
GROUP_ID = -1003785280527
ADMIN_ID = 8297497276

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
        keyboard=[[KeyboardButton(text="📮 ISHONCH QUTISI")]],
        resize_keyboard=True
    )

    inline = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Maktab yangiliklari 🗞️", url="https://t.me/pm_nam_imi")],
            [InlineKeyboardButton(text="Dasturchi 👨‍💻", url="https://t.me/saval_info_robot")]
        ]
    )

    await message.answer(
        "📮 ISHONCH QUTISI\n\nAriza yoki taklif yuborishingiz mumkin.",
        reply_markup=keyboard
    )

    await message.answer(
        "Qo‘shimcha ma'lumot:",
        reply_markup=inline
    )

@dp.message(F.text == "📮 ISHONCH QUTISI")
async def trust_box(message: types.Message, state: FSMContext):

    await message.answer(
        "Xabaringizni yuboring (matn, rasm yoki video).",
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

    text = f"📮 ISHONCH QUTISI\n\n💬 {message.text}"

    sent = await bot.send_message(GROUP_ID, text)

    add_message_link(sent.message_id, user_id)

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📮 ISHONCH QUTISI")]],
        resize_keyboard=True
    )

    await message.answer("✅ Xabaringiz yuborildi", reply_markup=keyboard)

    await state.clear()

@dp.message(TrustBox.waiting_for_message, F.photo)
async def send_photo(message: types.Message, state: FSMContext):

    photo = message.photo[-1].file_id

    sent = await bot.send_photo(
        GROUP_ID,
        photo,
        caption="📮 ISHONCH QUTISI\n\n🖼 Rasmli xabar"
    )

    add_message_link(sent.message_id, message.from_user.id)

    await message.answer("✅ Rasm yuborildi")

    await state.clear()

@dp.message(TrustBox.waiting_for_message, F.video)
async def send_video(message: types.Message, state: FSMContext):

    video = message.video.file_id

    sent = await bot.send_video(
        GROUP_ID,
        video,
        caption="📮 ISHONCH QUTISI\n\n🎥 Video xabar"
    )

    add_message_link(sent.message_id, message.from_user.id)

    await message.answer("✅ Video yuborildi")

    await state.clear()

@dp.message(F.chat.id == GROUP_ID, F.reply_to_message)
async def admin_reply(message: types.Message):

    replied = message.reply_to_message.message_id

    user_id = get_user_id(replied)

    if user_id:
        await bot.send_message(
            user_id,
            f"📩 Sizning murojaatingizga javob\n\n👨‍💻 Admin:\n{message.text}"
        )

        await message.reply("✅ Foydalanuvchiga yuborildi")

    else:
        await message.reply("❌ Foydalanuvchi topilmadi")

@dp.message(Command("stat"))
async def stats(message: types.Message):

    if message.from_user.id != ADMIN_ID:
        return

    db = load_messages_db()

    await message.answer(
        f"📊 Statistika\n\n📩 Murojaatlar soni: {len(db)}"
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
