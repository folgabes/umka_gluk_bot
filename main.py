import os
import asyncpg
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
)

API_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
CHANNEL_USERNAME = "@merkulyevy_live_evolution_space"
ADMIN_IDS = [123456789, 987654321]  # вставь сюда ID админов

bot = Bot(token=API_TOKEN, parse_mode="Markdown")
dp = Dispatcher(bot)

# ---------- БД ----------
async def create_tables():
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id BIGINT PRIMARY KEY,
        step TEXT,
        name TEXT,
        contact TEXT,
        email TEXT,
        gender TEXT,
        age TEXT,
        work_area TEXT,
        current INT DEFAULT 1
    );
    """)
    await conn.execute("""
    CREATE TABLE IF NOT EXISTS answers (
        id SERIAL PRIMARY KEY,
        user_id BIGINT REFERENCES users(user_id),
        lesson_id INT,
        answer TEXT
    );
    """)
    await conn.close()

async def get_user(user_id):
    conn = await asyncpg.connect(DATABASE_URL)
    row = await conn.fetchrow("SELECT * FROM users WHERE user_id=$1", user_id)
    await conn.close()
    return dict(row) if row else None

async def update_user(user_id, **kwargs):
    conn = await asyncpg.connect(DATABASE_URL)
    user = await get_user(user_id)
    if not user:
        await conn.execute(
            "INSERT INTO users (user_id, step, current) VALUES ($1, $2, $3)",
            user_id, kwargs.get("step", "ask_name"), kwargs.get("current", 1)
        )
    else:
        sets, values = [], []
        for i, (k, v) in enumerate(kwargs.items(), start=1):
            sets.append(f"{k} = ${i+1}")
            values.append(v)
        query = f"UPDATE users SET {', '.join(sets)} WHERE user_id=$1"
        await conn.execute(query, user_id, *values)
    await conn.close()

async def save_answer(user_id, lesson_id, answer):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute(
        "INSERT INTO answers (user_id, lesson_id, answer) VALUES ($1, $2, $3)",
        user_id, lesson_id, answer
    )
    await conn.close()

# ---------- УРОКИ ----------
lessons = {
    1: {"text": "📽 Урок 1...\n\n📝 Вопрос: ..."},
    2: {"text": "📽 Урок 2...\n\n📝 Вопрос: ..."},
    3: {"text": "📽 Урок 3...\n\n📝 Вопрос: ..."}
}

async def send_lesson(user_id, lesson_id):
    if lesson_id in lessons:
        await bot.send_message(user_id, lessons[lesson_id]["text"])
    else:
        await bot.send_message(user_id, "Курс завершён 🎉")

# ---------- ПОДПИСКА ----------
async def check_subscription(user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ---------- СТАРТ ----------
@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    user = await get_user(message.from_user.id)
    if not user:
        # новый → показать кнопку
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        keyboard.add(KeyboardButton("Начать"))
        await bot.send_message(
            message.chat.id,
            "Привет! 👋 Я бот для курса. Нажми кнопку, чтобы начать.",
            reply_markup=keyboard
        )
    else:
        await bot.send_message(message.chat.id, "Ты уже зарегистрирован, продолжаем 🚀")

@dp.message_handler(lambda m: m.text == "Начать")
async def handle_begin(message: types.Message):
    user_id = message.from_user.id
    await update_user(user_id, step="ask_name", current=1)
    await bot.send_message(
        message.chat.id,
        "Как тебя зовут?",
        reply_markup=ReplyKeyboardRemove()
    )

# ---------- АНКЕТА ----------
@dp.message_handler()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    user = await get_user(user_id)
    if not user:
        await update_user(user_id, step="ask_name")
        return await message.answer("Как тебя зовут?")

    step = user["step"]

    if step == "ask_name":
        await update_user(user_id, name=message.text.strip(), step="ask_contact")
        await message.answer("Оставь контакт: телефон или ник в Telegram.")

    elif step == "ask_contact":
        await update_user(user_id, contact=message.text.strip(), step="ask_email")
        await message.answer("И последнее — твой email:")

    elif step == "ask_email":
        await update_user(user_id, email=message.text.strip(), step="waiting_subscription")
        if await check_subscription(user_id):
            await update_user(user_id, step="lesson", current=1)
            await send_lesson(user_id, 1)
        else:
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("🔔 Подписаться", url="https://t.me/merkulyevy_live_evolution_space"))
            keyboard.add(InlineKeyboardButton("✅ Я подписался", callback_data="check_subscription"))
            await message.answer(
                "⚠️ Чтобы пройти курс, нужно быть подписанным. Подпишись и нажми «Я подписался».",
                reply_markup=keyboard
            )

    elif step == "lesson":
        current = user["current"]
        await save_answer(user_id, current, message.text.strip())
        await update_user(user_id, current=current+1)
        await send_lesson(user_id, current+1)

# ---------- КНОПКИ ----------
@dp.callback_query_handler(lambda c: c.data == "check_subscription")
async def process_subscription(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if await check_subscription(user_id):
        await update_user(user_id, step="lesson", current=1)
        await bot.send_message(user_id, "Отлично, подписка подтверждена ✨")
        await send_lesson(user_id, 1)
    else:
        await bot.send_message(user_id, "Пока не вижу подписки 🤔")

# ---------- ВЫГРУЗКА ----------
@dp.message_handler(commands=["export"])
async def export_cmd(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return await message.answer("⛔ У тебя нет доступа")
    conn = await asyncpg.connect(DATABASE_URL)
    rows = await conn.fetch("""
        SELECT u.user_id, u.name, u.email, a.lesson_id, a.answer
        FROM users u
        LEFT JOIN answers a ON u.user_id = a.user_id
        ORDER BY u.user_id, a.lesson_id
    """)
    await conn.close()
    text = "Экспорт:\n\n"
    for r in rows:
        text += f"{r['name']} ({r['email']}) | Урок {r['lesson_id']}: {r['answer']}\n"
    await message.answer(text or "Нет данных")

# ---------- ЗАПУСК ----------
if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_tables())
    executor.start_polling(dp, skip_updates=True)
