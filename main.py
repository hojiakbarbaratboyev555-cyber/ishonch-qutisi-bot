import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from fastapi import FastAPI
import uvicorn
import os

BOT_TOKEN = "8618077281:AAHCUmkUf9g6ZG56QxSLLl5F27of4eLR_YY"
GROUP_ID = -1003874749853  # Adminlar guruhi ID

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# =======================
# FSM State
# =======================
class TrustBox(StatesGroup):
    waiting_for_message = State()


# =======================
# User xabar ID mapping (anonim)
# =======================
user_messages = {}  # {guruh_xabar_id: user_id}


# =======================
# Reply keyboard (pastki 4 tugma)
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
        f"✨𝗔𝘀𝘀𝗮𝗹𝗼𝗺𝘂 𝗮𝗹𝗮𝘆𝗸𝘂𝗺: {message.from_user.full_name}\n"
        "🔰𝗕𝗼𝘁𝗶𝗺𝗶𝘇𝗴𝗮 𝘅𝘂𝘀𝗵 𝗸𝗲𝗹𝗶𝗯𝘀𝗶𝘇\n"
        "🤖𝗗𝗮𝘃𝗼𝗺 𝗲𝘁𝗶𝘀𝗵 𝘂𝗰𝗵𝘂𝗻 𝗾𝘂𝘆𝗶𝗱𝗮𝗴𝗶 𝘁𝘂𝗴𝗺𝗮𝗹𝗮𝗿𝗱𝗮𝗻 𝗳𝗼𝘆𝗱𝗮𝗹𝗮𝗻𝗶𝗻𝗴 👇",
        reply_markup=main_menu()
    )


# =======================
# Menu tugmalari handler
# =======================
@dp.message(TrustBox.waiting_for_message)
async def menu_handler(message: types.Message, state: FSMContext):
    text = message.text

    if text == "🏫 Maktabimiz haqida":
        await message.answer(
            "NAMANGAN SHAHAR 1-SON IXTISOSLASHTIRILGAN MAKTAB INTERNATI – KELAJAK TALABALARI MASKANI!\n\n2026-2027 o‘quv yili uchun \n\n🌟 Aniq va tabiiy fanlarga ixtisoslashgan maktab-internat 4- va 6-sinf bitiruvchilarini imtihonga taklif etadi!\n\n🎯 Maktab-internat afzalliklari: • Matematika, fizika, kimyo, biologiya va ingliz tili fanlari chuqurlashtirib o‘qitiladi\n• Zamonaviy jihozlangan fan laboratoriyalari\n• Malakali va fidoyi o‘qituvchilar\n• Darsdan tashqari to‘garaklar\n• Bepul yotoqxona\n• 5 mahal bepul ovqat\n• Muddatdan avval talabalik imkoniyati!\n\n🏆 OTMga kirish ko‘rsatkichlari:\n\n2023-yil bitiruvchilari: 100%\n(43 nafar – 25 ta grant, 18 ta kontrakt)\n\n2024-yil bitiruvchilari: 97%\n(69 nafar – 32 ta grant, 35 ta kontrakt)\n\n2025-yil bitiruvchilari: 100%\n(59 nafar – 30 ta grant, 29 ta kontrakt)\n\n🏫 Manzil: Namangan sh., Dashtbog‘ MFY, Sanoat ko‘chasi, 101-uy",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [types.InlineKeyboardButton(text="🔰Batafsil",
                                                url="https://t.me/pm_nam_imi")]
                ]
            )
        )

    elif text == "📝 Ariza topshirish":
        await message.answer(
            "📝Namangan shahar 1-son ixtisoslashtirilgan maktab internatiga ariza topshirish onlayn tarzda amalga oshiriladi\n\n🗒️Ariza toʻldirish qoidalari va shartlari bilan tanishib chiqing.\n\n📌Namangan shahar 1-IMIga ariza topshirish 2026-yil 1-20-iyun kunlari amalga oshirilishi kutilmoqda\n\nAriza berish👇",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [types.InlineKeyboardButton(text="📝Ariza berish",
                                                url="https://ariza.piima.uz")]
                ]
            )
        )

    elif text == "📮 Ishonch qutisi":
        await message.answer("📩 Habaringizni yuboring, adminlar siz bilan bogʻlanadi.\n\nBilib qoʻying sizning shaxsingiz sir saqlanadi 🤐\nXech narsadan qoʻrqmang va fikringizni erkin bayon qiling")
        await state.set_state(TrustBox.waiting_for_message)

    elif text == "👨‍💻 Adminlar bilan bogʻlanish":
        await message.answer(
            "ADMINGA HABAR BOʻLIMI\n\nSiz bu boʻlim orqali bot haqida savollarga javob topishingiz mumkin\n\nPastdagi tugmadan foydalaning👇",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [types.InlineKeyboardButton(text="☎️Murojaat qilish",
                                                url="https://t.me/axe_adm_bot?start=1")]
                ]
            )
        )


# =======================
# Ishonch qutisi xabari → guruhga anonim yuborish
# =======================
@dp.message(lambda message: message.text and message.text not in [
    "🏫 Maktabimiz yangiliklari",
    "📝 Ariza topshirish",
    "👨‍💻 Adminlar bilan bogʻlanish",
    "📮 Ishonch qutisi"
])
async def send_to_group_anonymous(message: types.Message):
    sent_msg = await bot.send_message(GROUP_ID, f"📮Ishonch qutisi:\n{message.text}")
    user_messages[sent_msg.message_id] = message.from_user.id


# =======================
# Admin reply → foydalanuvchiga yetkazish
# =======================
@dp.message(lambda message: message.chat.id == GROUP_ID and message.reply_to_message)
async def reply_to_user(message: types.Message):
    replied_id = message.reply_to_message.message_id
    user_id = user_messages.get(replied_id)
    if user_id:
        await bot.send_message(user_id, f"📩 Admin javobi:\n{message.text}")


# =======================
# FastAPI + polling
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


@dp.message(Command("start"))
async def start(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📮 𝗜𝗦𝗛𝗢𝗡𝗖𝗛 𝗤𝗨𝗧𝗜𝗦𝗜")]],
        resize_keyboard=True
    )

    inline = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="𝗠𝗔𝗞𝗧𝗔𝗕 𝗬𝗔𝗡𝗚𝗜𝗟𝗜𝗞𝗟𝗔𝗥𝗜 🗞️", url="https://t.me/pm_nam_imi")],
            [InlineKeyboardButton(text="𝗔𝗗𝗠𝗜𝗡𝗜𝗦𝗧𝗥𝗔𝗧𝗢𝗥𝗦 👨‍💻", url="https://t.me/axe_adm_bot")]
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


# ✅ FIX: F.text olib tashlandi
@dp.message(TrustBox.waiting_for_message)
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

    await message.answer(
        "✅ Xabaringiz yuborildi. Tez orada javob xati keladi. Sizdan kutishingizni iltimos qilamiz",
        reply_markup=keyboard
    )

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
    # ✅ FIX: conflict yo‘q qilish
    await bot.delete_webhook(drop_pending_updates=True)
    asyncio.create_task(dp.start_polling(bot, skip_updates=True))


@app.get("/")
def home():
    return {"status": "Bot ishlayapti"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
