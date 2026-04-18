Import asyncio
import logging
import json
import os

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from fastapi import FastAPI
import uvicorn

# =======================
# SOZLAMALAR
# =======================
BOT_TOKEN = "8760367023:AAF77kDhiO9Up_WxTlZseiIR-Jh2b1Wv8SY"
GROUP_ID = -1003874749853
MESSAGES_DB_FILE = "messages_db.json"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# =======================
# FSM State
# =======================
class TrustBox(StatesGroup):
    waiting_for_message = State()

# =======================
# MA'LUMOTLAR BAZASI (JSON)
# =======================
def load_messages():
    if os.path.exists(MESSAGES_DB_FILE):
        try:
            with open(MESSAGES_DB_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}

def save_messages(data):
    try:
        with open(MESSAGES_DB_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        logging.error(f"Bazaga yozishda xatolik: {e}")

def add_link(msg_id, user_id):
    data = load_messages()
    data[str(msg_id)] = user_id
    save_messages(data)

def get_user(msg_id):
    data = load_messages()
    return data.get(str(msg_id))

# =======================
# MENU TUGMALARI
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
# START KOMANDASI
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
        await message.answer(
            "NAMANGAN SHAHAR 1-SON IXTISOSLASHTIRILGAN MAKTAB INTERNATI – KELAJAK TALABALARI MASKANI!\n\n2026-2027 o‘quv yili uchun \n\n🌟 Aniq va tabiiy fanlarga ixtisoslashtirilgan maktab-internat 4- va 6-sinf bitiruvchilarini imtihonga taklif etadi!\n\n🎯 Maktab-internat afzalliklari: • Matematika, fizika, kimyo, biologiya va ingliz tili fanlari chuqurlashtirib o‘qitiladi\n• Zamonaviy jihozlangan fan laboratoriyalari\n• Malakali va fidoyi o‘qituvchilar\n• Darsdan tashqari to‘garaklar\n• Bepul yotoqxona\n• 5 mahal bepul ovqat\n• Muddatdan avval talabalik imkoniyati!\n\n🏆 OTMga kirish ko‘rsatkichlari...\n\n🏫 Manzil: Namangan sh., Dashtbog‘ MFY, Sanoat ko‘chasi, 101-uy",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[[types.InlineKeyboardButton(text="🔰 Batafsil", url="https://t.me/pm_nam_imi")]]
            )
        )
    elif message.text == "📝 Ariza topshirish":
        await message.answer(
            "📝Namangan shahar 1-son ixtisoslashtirilgan maktab internatiga ariza topshirish onlayn tarzda amalga oshiriladi\n\n🧾Ariza topshirish qoidalari va shartlari bilan tanishib chiqing.\n\n📌Namangan shahar 1-IMIga ariza topshirish 2026-yil 1-20-iyun kunlari amalga oshirilishi kutilmoqda (rasman tasdiqlanmagan)\n\nAriza topshirish👇",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[[types.InlineKeyboardButton(text="📝 Ariza berish", url="https://ariza.piima.uz")]]
            )
        )
    elif message.text == "📮 Ishonch qutisi":
        await message.answer(
            "📩 Ishonch qutisi\n\n🏫Siz bu tizimda maktabimiz maʼmuriyatiga oʻz savollaringizni yuborishingiz mumkin\n👤Sizning shaxsingiz sir saqlanadi\n\n📝Xabaringizni yuboring",
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.set_state(TrustBox.waiting_for_message)
    elif message.text == "👨‍💻 Adminlar bilan bogʻlanish":
        await message.answer(
            "🔍Bu boʻlimda siz bot haqida savollarga botning yaratuvchilaridan javob olasiz\n☎️Pastdagi tugma orqali davom eting",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[[types.InlineKeyboardButton(text="☎️ Murojaat qilish", url="https://t.me/axe_adm_bot")]]
            )
        )

# =======================
# ISHONCH QUTISI (XABAR YUBORISH)
# =======================
@dp.message(TrustBox.waiting_for_message)
async def send_anonymous(message: types.Message, state: FSMContext):
    if not message.text:
        await message.answer("Iltimos, faqat matnli xabar yuboring.")
        return

    # Guruhga yuborish
    sent = await bot.send_message(
        GROUP_ID,
        f"📮 #Ishonch_qutisi\n\n💬 {message.text}"
    )

    # Xabar ID va foydalanuvchi ID sini bog'lab saqlash
    add_link(sent.message_id, message.from_user.id)
    
    await message.answer("✅ Xabaringiz yuborildi. Admin javobini kuting.", reply_markup=main_menu())
    await state.clear()

# =======================
# ADMIN JAVOBI (GURUHDA REPLY QILINSA)
# =======================
@dp.message(F.chat.id == GROUP_ID, F.reply_to_message)
async def admin_reply(message: types.Message):
    # Reply qilingan xabarning ID sini olish
    replied_id = message.reply_to_message.message_id
    
    # Bazadan ushbu xabarni yuborgan foydalanuvchini topish
    user_id = get_user(replied_id)

    if user_id:
        try:
            await bot.send_message(
                chat_id=user_id,
                text=f"📩 Admin javobi:\n\n{message.text}"
            )
            await message.reply("✅")
        except Exception as e:
            logging.error(f"Xabar yuborishda xatolik: {e}")

# =======================
# FastAPI & RUN
# =======================
app = FastAPI()

@app.on_event("startup")
async def on_startup():
    await bot.delete_webhook(drop_pending_updates=True)
    asyncio.create_task(dp.start_polling(bot))

@app.get("/")
def home():
    return {"status": "Bot ishlayapti"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
