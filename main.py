import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from fastapi import FastAPI
import uvicorn
import os

BOT_TOKEN = "8618077281:AAFT5I3JWXazPhs3x8FgXF6QrsSOHr58njE"
GROUP_ID = -1003874749853

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# =======================
# FSM State
# =======================
class TrustBox(StatesGroup):
    waiting_for_message = State()

# =======================
# user mapping
# =======================
user_messages = {}  # {(msg_id, thread_id): user_id}

# =======================
# menu
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
# start
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
# menu handler
# =======================
@dp.message(StateFilter(None))
async def menu_handler(message: types.Message, state: FSMContext):

    if message.text == "🏫 Maktabimiz haqida":
        await message.answer(
            "NAMANGAN SHAHAR 1-SON IXTISOSLASHTIRILGAN MAKTAB INTERNATI – KELAJAK TALABALARI MASKANI!\n\n2026-2027 o‘quv yili uchun \n\n🌟 Aniq va tabiiy fanlarga ixtisoslashtirilgan maktab-internat 4- va 6-sinf bitiruvchilarini imtihonga taklif etadi!\n\n🎯 Maktab-internat afzalliklari: • Matematika, fizika, kimyo, biologiya va ingliz tili fanlari chuqurlashtirib o‘qitiladi\n• Zamonaviy jihozlangan fan laboratoriyalari\n• Malakali va fidoyi o‘qituvchilar\n• Darsdan tashqari to‘garaklar\n• Bepul yotoqxona\n• 5 mahal bepul ovqat\n• Muddatdan avval talabalik imkoniyati!\n\n🏫 Manzil: Namangan sh., Dashtbog‘ MFY, Sanoat ko‘chasi, 101-uy"
        )

    elif message.text == "📮 Ishonch qutisi":
        await message.answer(
            "📩 Ishonch qutisi\n\nXabar yuboring",
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.set_state(TrustBox.waiting_for_message)

# =======================
# anonim xabar
# =======================
@dp.message(TrustBox.waiting_for_message)
async def send_anonymous(message: types.Message, state: FSMContext):

    sent = await bot.send_message(
        GROUP_ID,
        f"📮 Ishonch qutisi\n\n{message.text}"
    )

    user_messages[(sent.message_id, sent.message_thread_id)] = message.from_user.id

    await message.answer(
        "✅ Xabaringiz yuborildi\nAdmin javobini kuting",
        reply_markup=main_menu()
    )

    await state.clear()

# =======================
# admin reply
# =======================
@dp.message()
async def admin_reply(message: types.Message):

    if message.chat.id != GROUP_ID:
        return

    if not message.reply_to_message:
        return

    key = (
        message.reply_to_message.message_id,
        message.reply_to_message.message_thread_id
    )

    user_id = user_messages.get(key)

    if not user_id:
        return

    await bot.send_message(
        user_id,
        f"📩 Admin javobi:\n\n{message.text}"
    )

    await message.reply("✅")

# =======================
# FastAPI
# =======================
app = FastAPI()

@app.on_event("startup")
async def on_startup():
    await bot.delete_webhook(drop_pending_updates=True)
    asyncio.create_task(dp.start_polling(bot))

@app.get("/")
def home():
    return {"status": "Bot ishlayapti"}

# =======================
# run
# =======================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
