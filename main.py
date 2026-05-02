import asyncio
import logging
import json
import os

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Update

from fastapi import FastAPI, Request
import uvicorn

# =======================
# SOZLAMALAR
# =======================
BOT_TOKEN = "8760367023:AAG6c9t11ghRC-QotfurmhGdXir7KLueu5s"
WEBHOOK_HOST = "https://ishonch-qutisi-bot.onrender.com"
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

GROUP_ID = -1003874749853
MESSAGES_DB_FILE = "messages_db.json"

PORT = int(os.environ.get("PORT", 10000))

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# =======================
# RASMLAR
# =======================
IMAGE_TRUSTBOX = "1776531646947.png"
IMAGE_ADMIN = "file_000000005eb872439ca0c31a72a81d4f.png"
IMAGE_ARIZA = "IMG_20260502_164937_557.jpg"
IMAGE_SCHOOL = "1776531637585.png"

# =======================
# FSM STATE
# =======================
class TrustBox(StatesGroup):
    waiting_for_message = State()

# =======================
# DB
# =======================
def load_messages():
    if os.path.exists(MESSAGES_DB_FILE):
        try:
            with open(MESSAGES_DB_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_messages(data):
    with open(MESSAGES_DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def add_link(msg_id, user_id):
    data = load_messages()
    data[str(msg_id)] = user_id
    save_messages(data)

def get_user(msg_id):
    data = load_messages()
    return data.get(str(msg_id))

# =======================
# MENU
# =======================
def main_menu():
    return types.ReplyKeyboardMarkup(
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

# =======================
# START
# =======================
@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"✨ Assalomu alaykum: {message.from_user.full_name}\n"
        "🔰 Botimizga xush kelibsiz\n"
        "👇 Kerakli bo‘limni tanlang",
        reply_markup=main_menu()
    )

# =======================
# MENU HANDLER
# =======================
@dp.message(StateFilter(None), F.text.in_({"🏫 Maktabimiz haqida", "📝 Ariza topshirish", "📮 Ishonch qutisi", "👨‍💻 Adminlar bilan bogʻlanish"}))
async def menu_handler(message: types.Message, state: FSMContext):

    if message.text == "🏫 Maktabimiz haqida":
        await message.answer_photo(
            photo=types.FSInputFile(IMAGE_SCHOOL),
            caption="NAMANGAN SHAHAR 1-SON IXTISOSLASHTIRILGAN MAKTAB INTERNATI – KELAJAK TALABALARI MASKANI!\n\n2026-2027 o‘quv yili uchun \n\n🌟 Aniq va tabiiy fanlarga ixtisoslashtirilgan maktab-internat 4- va 6-sinf bitiruvchilarini imtihonga taklif etadi!\n\n🎯 Maktab-internat afzalliklari:\n• Matematika, fizika, kimyo, biologiya va ingliz tili fanlari chuqurlashtirib o‘qitiladi\n• Zamonaviy jihozlangan fan laboratoriyalari\n• Malakali va fidoyi o‘qituvchilar\n• Darsdan tashqari to‘garaklar\n• Bepul yotoqxona\n• 5 mahal bepul ovqat\n• Muddatdan avval talabalik imkoniyati!\n\n🏆 OTMga kirish ko‘rsatkichlari yuqori\n\n🏫 Manzil: Namangan sh., Dashtbog‘ MFY, Sanoat ko‘chasi, 101-uy",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[[types.InlineKeyboardButton(text="🔰 Batafsil", url="https://t.me/pm_nam_imi")]]
            )
        )

    elif message.text == "📝 Ariza topshirish":
        await message.answer_photo(
            photo=types.FSInputFile(IMAGE_ARIZA),
            caption="📣DIQQAT, E'LON!\n🏢Ixtisoslashtirilgan ta'lim muassasalari agentligi tizimidagi barcha maktablar, shu jumladan Namangan shahar 1-son  ixtisoslashtirilgan maktab-internatiga 2026-2027 o'quv yili uchun qabul boshlanmoqda! \n☎️ Namangan shahar 1-son  ixtisoslashtirilgan maktab-internatida 1-15-mayga qadar MUROJAATLAR MARKAZI kelib o'zingizni qiziqtirgan savollarga javob olishingiz mumkin.\n📅  Hujjatlar 15-maydan 4-iyungacha my.gov.uz va ariza.piima.uz sahifasi orqali onlayn qabul qilinadi.\nMa'lumot o'rnida yangi o'quv yiliga maktab uchun qabul quyidagi sinflar kesimida bo'ladi:\n✅5-sinf (aniq fanlar) uchun 2 ta sinf; har bir sinfga 24 nafar\n✅7-sinf (tabiiy fanlar) uchun; 1 ta sinf  24 nafar\n✅10-sinf (aniq fanlar) uchun; 5 bo'sh o'rin\n✅10-sinf (tabiiy fanlar) uchun; 4 bo'sh o'rin\nJarayon bo'yicha o'zingizni qiziqtirgan savollar bilan quyidagi manzilga murojaat qilishingiz mumkin: \nt.me/Namangan_1_imi_qabul_2026\nMurojaatlar markazi telefon raqamlari: \n+998932644000\n+998939273194",
        )

    elif message.text == "📮 Ishonch qutisi":
        await message.answer_photo(
            photo=types.FSInputFile(IMAGE_TRUSTBOX),
            caption="📩 Ishonch qutisi\n\n🏫 Siz bu tizimda maktabimiz maʼmuriyatiga oʻz savollaringizni yuborishingiz mumkin\n👤 Sizning shaxsingiz sir saqlanadi\n\n📝 Xabaringizni yuboring",
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.set_state(TrustBox.waiting_for_message)

    elif message.text == "👨‍💻 Adminlar bilan bogʻlanish":
        await message.answer_photo(
            photo=types.FSInputFile(IMAGE_ADMIN),
            caption="🔍 Bu boʻlimda siz bot haqida savollarga botning yaratuvchilaridan javob olasiz\n📌 ❗ Bot ishlamay qolsa ham shu yerga murojaat qiling. Shuning uchun ham bu botni yoʻqotib qoʻymang\n\n☎️ Pastdagi tugma orqali davom eting",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[[types.InlineKeyboardButton(text="☎️ Murojaat", url="https://t.me/HB7410_bot")]]
            )
        )

# =======================
# ISHONCH QUTISI
# =======================
@dp.message(TrustBox.waiting_for_message)
async def send_anonymous(message: types.Message, state: FSMContext):

    sent = await bot.send_message(
        GROUP_ID,
        f"📮 #Ishonch_qutisi\n\n💬 {message.text}"
    )

    add_link(sent.message_id, message.from_user.id)

    await message.answer(
        "✅ Xabaringiz yuborildi\n⏳ Maktab javobini kuting",
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
        await bot.send_message(user_id, f"📩 Admin javobi:\n\n💬 {message.text}")
        await message.reply("✅")

# =======================
# FASTAPI (WEBHOOK)
# =======================
app = FastAPI()

@app.on_event("startup")
async def startup():
    await bot.set_webhook(WEBHOOK_URL)

@app.post(WEBHOOK_PATH)
async def webhook(request: Request):
    data = await request.json()
    update = Update.model_validate(data)
    await dp.feed_update(bot, update)
    return {"ok": True}

@app.get("/")
async def home():
    return {"status": "Bot ishlayapti"}

# =======================
# RUN
# =======================
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
