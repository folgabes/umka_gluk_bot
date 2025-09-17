from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import asyncpg
import asyncio
import os

API_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = "@merkulyevy_live_evolution_space"

ADMINS = [123456789, 987654321]  # сюда подставь свои id

bot = Bot(token=API_TOKEN, parse_mode="Markdown")
dp = Dispatcher(bot)

# ---------- БАЗА ДАННЫХ ----------
async def create_pool():
    return await asyncpg.create_pool(
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD"),
        database=os.getenv("PGDATABASE"),
        host=os.getenv("PGHOST"),
        port=os.getenv("PGPORT"),
    )

pool = None

async def init_db():
    async with pool.acquire() as conn:
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id BIGINT PRIMARY KEY,
            name TEXT,
            contact TEXT,
            email TEXT,
            gender TEXT,
            age TEXT,
            work_area TEXT,
            step TEXT DEFAULT 'ask_name',
            current INT DEFAULT 1
        )
        """)
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS answers (
            user_id BIGINT,
            lesson_num INT,
            answer TEXT,
            PRIMARY KEY(user_id, lesson_num)
        )
        """)

async def get_user(user_id):
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM users WHERE id=$1", user_id)
        if row:
            return dict(row)
        else:
            await conn.execute("INSERT INTO users(id) VALUES($1)", user_id)
            return {"id": user_id, "step": "ask_name", "current": 1}

async def update_user(user_id, **fields):
    async with pool.acquire() as conn:
        sets = ", ".join([f"{k}=${i+2}" for i, k in enumerate(fields.keys())])
        values = list(fields.values())
        await conn.execute(f"UPDATE users SET {sets} WHERE id=$1", user_id, *values)

async def save_answer(user_id, lesson_num, answer):
    async with pool.acquire() as conn:
        await conn.execute("""
        INSERT INTO answers(user_id, lesson_num, answer)
        VALUES ($1, $2, $3)
        ON CONFLICT (user_id, lesson_num) DO UPDATE SET answer=$3
        """, user_id, lesson_num, answer)

async def get_answers(user_id):
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT lesson_num, answer FROM answers WHERE user_id=$1 ORDER BY lesson_num", user_id)
        return {str(r["lesson_num"]): r["answer"] for r in rows}

# ---------- ПРОВЕРКА ПОДПИСКИ ----------
async def check_subscription(user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ---------- УРОКИ ----------
lessons = {
    1: {
        "question": "Вспомни, пожалуйста, какие преодолённые тобой трудности укрепили твоё здоровье и помогли обрести внутреннюю силу и спокойствие?",
        "text": "📽 Урок 1. Здоровье можно поменять на деньги\n\n🔗 [Rutube](https://rutube.ru/video/private/438c67c0e3510477ba92ef1c9cbda807/?p=m8ZK3IF63nq3U8aiuKBfyQ)\n🔗 [YouTube](https://youtube.com/shorts/_uTHQopErp4)\n\n---\n\n📝 Задание:\n\nВспомни, пожалуйста, какие преодолённые тобой трудности укрепили твоё здоровье и помогли обрести внутреннюю силу и спокойствие?",
    },
    2: {
        "question": "Расскажи о моментах в своей жизни, когда деньги принесли тебе настоящее счастье и радость. Были ли эпизоды, когда обладание ими стало источником огорчений и переживаний?",
        "text": "📽 Урок 2. Деньги могут спасти от старости и смерти\n\n🔗 [Rutube](https://rutube.ru/video/private/a455fedbc14d98eeac76e09dec70aaa8/?p=O-rFwwAB4tvSNHOJK5gDgw)\n🔗 [YouTube](https://youtube.com/shorts/6KOFfzMXeBo)\n\n---\n\n📝 Задание:\n\nРасскажи о моментах в своей жизни, когда деньги принесли тебе настоящее счастье и радость. Были ли эпизоды, когда обладание ими стало источником огорчений и переживаний?",
    },
    # ... уроки 3–5 по аналогии ...
}

async def send_lesson(user_id, lesson_id):
    lesson = lessons.get(lesson_id)
    if lesson:
        await bot.send_message(user_id, lesson["text"])
    else:
        await bot.send_message(user_id, "🎉 Курс завершён! Напиши /answers, чтобы посмотреть свои ответы.")

# ---------- КОМАНДЫ ----------
@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    await update_user(message.from_user.id, step="ask_name", current=1)
    await message.answer("👋 Привет! Это бот для мини-курса *Глюки про деньги*.\n\nКак тебя зовут?")

@dp.message_handler(commands=["reset"])
async def reset_cmd(message: types.Message):
    await update_user(message.from_user.id, step="ask_name", current=1)
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM answers WHERE user_id=$1", message.from_user.id)
    await message.answer("Прогресс обнулён. Напиши /start, чтобы начать заново.")

@dp.message_handler(commands=["answers"])
async def answers_cmd(message: types.Message):
    answers = await get_answers(message.from_user.id)
    if not answers:
        await message.answer("У тебя пока нет сохранённых ответов ✍️")
        return
    text = "📒 Твои ответы:\n\n"
    for num, ans in answers.items():
        question = lessons[int(num)]["question"]
        text += f"📽 Урок {num}. {question}\nОтвет: {ans}\n\n"
    await message.answer(text)

@dp.message_handler(commands=["export"])
async def export_cmd(message: types.Message):
    if message.from_user.id not in ADMINS:
        await message.answer("У тебя нет прав.")
        return
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT user_id, lesson_num, answer FROM answers ORDER BY user_id, lesson_num")
    text = "📦 Все ответы:\n\n"
    for r in rows:
        text += f"👤 {r['user_id']} | Урок {r['lesson_num']} | {r['answer']}\n"
    await message.answer(text or "Нет данных.")

# ---------- АНКЕТА ----------
gender_options = ["Мужчина", "Женщина"]
age_options = ["до 20", "20-30", "31-45", "46-60", "больше 60"]
work_options = ["Предприниматель", "Свой бизнес", "Фрилансер",
                "Руководитель в найме", "Сотрудник в найме", "Не работаю"]

@dp.message_handler()
async def handle_message(message: types.Message):
    user = await get_user(message.from_user.id)
    step = user["step"]

    if step == "ask_name":
        await update_user(message.from_user.id, name=message.text.strip(), step="ask_contact")
        await message.answer("Оставь контакт: телефон или ник в Telegram.")

    elif step == "ask_contact":
        await update_user(message.from_user.id, contact=message.text.strip(), step="ask_email")
        await message.answer("И последнее — твой email:")

    elif step == "ask_email":
        await update_user(message.from_user.id, email=message.text.strip(), step="ask_gender")
        kb = InlineKeyboardMarkup()
        for g in gender_options:
            kb.add(InlineKeyboardButton(g, callback_data=f"gender:{g}"))
        await message.answer("Прежде чем начать, напиши пару слов о себе.\n\nТы мужчина или женщина?", reply_markup=kb)

    elif step == "lesson":
        current = user["current"]
        await save_answer(message.from_user.id, current, message.text.strip())
        next_lesson = current + 1
        await update_user(message.from_user.id, current=next_lesson)
        await send_lesson(message.from_user.id, next_lesson)

# ---------- CALLBACK ----------
@dp.callback_query_handler(lambda c: c.data.startswith("gender:"))
async def process_gender(callback_query: CallbackQuery):
    gender = callback_query.data.split(":", 1)[1]
    await update_user(callback_query.from_user.id, gender=gender, step="ask_age")
    kb = InlineKeyboardMarkup()
    for a in age_options:
        kb.add(InlineKeyboardButton(a, callback_data=f"age:{a}"))
    await bot.send_message(callback_query.from_user.id, "Выбери свой возраст:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("age:"))
async def process_age(callback_query: CallbackQuery):
    age = callback_query.data.split(":", 1)[1]
    await update_user(callback_query.from_user.id, age=age, step="ask_work_area")
    kb = InlineKeyboardMarkup()
    for w in work_options:
        kb.add(InlineKeyboardButton(w, callback_data=f"work:{w}"))
    await bot.send_message(callback_query.from_user.id, "Выбери свою сферу деятельности:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("work:"))
async def process_work(callback_query: CallbackQuery):
    work = callback_query.data.split(":", 1)[1]
    await update_user(callback_query.from_user.id, work_area=work)
    # проверка подписки сразу
    if await check_subscription(callback_query.from_user.id):
        await update_user(callback_query.from_user.id, step="lesson", current=1)
        await bot.send_message(callback_query.from_user.id, "👍 Подписка уже есть. Начинаем курс!")
        await send_lesson(callback_query.from_user.id, 1)
    else:
        await update_user(callback_query.from_user.id, step="waiting_subscription")
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("🔔 Подписаться на канал", url="https://t.me/merkulyevy_live_evolution_space"))
        kb.add(InlineKeyboardButton("✅ Я подписался", callback_data="check_subscription"))
        await bot.send_message(callback_query.from_user.id,
                               "⚠️ Чтобы пройти курс, нужно подписаться на канал.\n\nПодпишись и нажми «Я подписался».",
                               reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data == "check_subscription")
async def process_subscription(callback_query: CallbackQuery):
    if await check_subscription(callback_query.from_user.id):
        await update_user(callback_query.from_user.id, step="lesson", current=1)
        await bot.send_message(callback_query.from_user.id, "Отлично, подписка подтверждена ✨ Начинаем курс!")
        await send_lesson(callback_query.from_user.id, 1)
    else:
        await bot.send_message(callback_query.from_user.id, "Пока не вижу подписки 🤔 Проверь ещё раз и нажми «Я подписался».")

# ---------- ЗАПУСК ----------
async def on_startup(dp):
    global pool
    pool = await create_pool()
    await init_db()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(on_startup(dp))
    executor.start_polling(dp, skip_updates=True)
