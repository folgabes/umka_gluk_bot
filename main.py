import os
import asyncpg
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

API_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

bot = Bot(token=API_TOKEN, parse_mode="Markdown")
dp = Dispatcher(bot)

CHANNEL_USERNAME = "@merkulyevy_live_evolution_space"
ADMIN_IDS = [123456789, 987654321]  # замени на свои id

# ---------------- УРОКИ ----------------
lessons = {
    1: {"question": "Вспомни трудности, которые укрепили твоё здоровье?",
        "text": "📽 Урок 1. Здоровье можно поменять на деньги\n\n[YouTube](https://youtube.com/shorts/_uTHQopErp4)"},
    2: {"question": "Расскажи о моментах счастья и огорчений, связанных с деньгами?",
        "text": "📽 Урок 2. Деньги могут спасти от старости\n\n[YouTube](https://youtube.com/shorts/6KOFfzMXeBo)"},
    3: {"question": "Поделись историей о случайных деньгах. Какой вывод ты сделал?",
        "text": "📽 Урок 3. Лёгкие деньги легко даются\n\n[YouTube](https://youtube.com/shorts/nzpJTNZseH8)"},
    4: {"question": "Какие действия уберегут тебя от потери денег?",
        "text": "📽 Урок 4. Деньги можно сохранить\n\n[YouTube](https://youtube.com/shorts/nzpJTNZseH8)"},
    5: {"question": "Какие ценности остаются без денег?",
        "text": "📽 Урок 5. Купи сейчас, заплатишь потом\n\n[YouTube](https://youtube.com/shorts/wkbbH1NzmdY)"}
}

# ---------------- АНКЕТА ----------------
gender_options = ["Мужчина", "Женщина"]
age_options = ["до 20", "20-30", "31-45", "46-60", "больше 60"]
work_options = ["Предприниматель", "Свой бизнес", "Фрилансер",
                "Руководитель в найме", "Сотрудник в найме", "Не работаю"]

# ---------------- БАЗА ----------------
async def init_db():
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id BIGINT PRIMARY KEY,
        name TEXT,
        contact TEXT,
        email TEXT,
        gender TEXT,
        age TEXT,
        work_area TEXT,
        step TEXT,
        current INT DEFAULT 1
    );
    """)
    await conn.execute("""
    CREATE TABLE IF NOT EXISTS answers (
        user_id BIGINT,
        lesson_id INT,
        answer TEXT,
        PRIMARY KEY (user_id, lesson_id)
    );
    """)
    await conn.close()

async def get_user(user_id):
    conn = await asyncpg.connect(DATABASE_URL)
    user = await conn.fetchrow("SELECT * FROM users WHERE user_id=$1", user_id)
    if not user:
        await conn.execute("INSERT INTO users(user_id, step) VALUES($1, $2)", user_id, "ask_name")
        user = await conn.fetchrow("SELECT * FROM users WHERE user_id=$1", user_id)
    await conn.close()
    return dict(user)

async def update_user(user_id, **fields):
    conn = await asyncpg.connect(DATABASE_URL)
    for k, v in fields.items():
        await conn.execute(f"UPDATE users SET {k}=$1 WHERE user_id=$2", v, user_id)
    await conn.close()

async def save_answer(user_id, lesson_id, answer):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("""
        INSERT INTO answers(user_id, lesson_id, answer)
        VALUES($1,$2,$3)
        ON CONFLICT (user_id, lesson_id) DO UPDATE SET answer=$3
    """, user_id, lesson_id, answer)
    await conn.close()

async def get_answers(user_id):
    conn = await asyncpg.connect(DATABASE_URL)
    rows = await conn.fetch("SELECT * FROM answers WHERE user_id=$1 ORDER BY lesson_id", user_id)
    await conn.close()
    return rows

# ---------------- ПОДПИСКА ----------------
async def check_subscription(user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ---------------- КОМАНДЫ ----------------
@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    await update_user(message.from_user.id, step="ask_name")
    await message.answer("👋 Привет! Это бот для мини-курса *Глюки про деньги*.\n\nКак тебя зовут?")

@dp.message_handler(commands=["reset"])
async def reset_cmd(message: types.Message):
    await update_user(message.from_user.id, step="ask_name", current=1)
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("DELETE FROM answers WHERE user_id=$1", message.from_user.id)
    await conn.close()
    await message.answer("Прогресс обнулён. Напиши /start, чтобы начать заново.")

@dp.message_handler(commands=["help"])
async def help_cmd(message: types.Message):
    for admin in ADMIN_IDS:
        await bot.send_message(admin, f"🆘 Помощь от @{message.from_user.username} ({message.from_user.id})")
    await message.answer("Запрос отправлен куратору. Мы скоро свяжемся с тобой.")

@dp.message_handler(commands=["answers"])
async def answers_cmd(message: types.Message):
    rows = await get_answers(message.from_user.id)
    if not rows:
        await message.answer("У тебя пока нет сохранённых ответов ✍️")
        return
    text = "📒 Твои ответы по курсу:\n\n"
    for r in rows:
        q = lessons[r["lesson_id"]]["question"]
        text += f"📽 Урок {r['lesson_id']}. {q}\nОтвет: {r['answer']}\n\n"
    await message.answer(text)

@dp.message_handler(commands=["export"])
async def export_cmd(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    conn = await asyncpg.connect(DATABASE_URL)
    rows = await conn.fetch("SELECT * FROM answers")
    await conn.close()
    text = "\n".join([f"{r['user_id']} | {r['lesson_id']} | {r['answer']}" for r in rows])
    await message.answer(f"Экспорт:\n{text[:4000]}")

# ---------------- АНКЕТА ----------------
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
        keyboard = InlineKeyboardMarkup()
        for g in gender_options:
            keyboard.add(InlineKeyboardButton(g, callback_data=f"gender:{g}"))
        await message.answer("Ты мужчина или женщина?", reply_markup=keyboard)

    elif step == "lesson":
        current = user["current"]
        if current > len(lessons):
            await message.answer("Курс завершён 🎉 Напиши /answers, чтобы посмотреть свои ответы.")
            return
        await save_answer(message.from_user.id, current, message.text.strip())
        await update_user(message.from_user.id, current=current + 1)
        await send_lesson(message.from_user.id, current + 1)

# ---------------- CALLBACK ----------------
@dp.callback_query_handler(lambda c: c.data.startswith("gender:"))
async def process_gender(callback_query: CallbackQuery):
    gender = callback_query.data.split(":", 1)[1]
    await update_user(callback_query.from_user.id, gender=gender, step="ask_age")
    keyboard = InlineKeyboardMarkup()
    for a in age_options:
        keyboard.add(InlineKeyboardButton(a, callback_data=f"age:{a}"))
    await bot.send_message(callback_query.from_user.id, "Выбери свой возраст:", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith("age:"))
async def process_age(callback_query: CallbackQuery):
    age = callback_query.data.split(":", 1)[1]
    await update_user(callback_query.from_user.id, age=age, step="ask_work_area")
    keyboard = InlineKeyboardMarkup()
    for w in work_options:
        keyboard.add(InlineKeyboardButton(w, callback_data=f"work:{w}"))
    await bot.send_message(callback_query.from_user.id, "Выбери свою сферу деятельности:", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith("work:"))
async def process_work(callback_query: CallbackQuery):
    work = callback_query.data.split(":", 1)[1]
    if await check_subscription(callback_query.from_user.id):
        await update_user(callback_query.from_user.id, work_area=work, step="lesson", current=1)
        await bot.send_message(callback_query.from_user.id, "✨ Подписка подтверждена. Начинаем курс!")
        await send_lesson(callback_query.from_user.id, 1)
    else:
        await update_user(callback_query.from_user.id, work_area=work, step="waiting_subscription")
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("🔔 Подписаться на канал", url="https://t.me/merkulyevy_live_evolution_space"))
        keyboard.add(InlineKeyboardButton("✅ Я подписался", callback_data="check_subscription"))
        await bot.send_message(callback_query.from_user.id,
            "⚠️ Чтобы пройти курс, нужно быть подписанным на канал.\n\nПодпишись и нажми «Я подписался».",
            reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == "check_subscription")
async def process_subscription(callback_query: CallbackQuery):
    if await check_subscription(callback_query.from_user.id):
        await update_user(callback_query.from_user.id, step="lesson", current=1)
        await bot.send_message(callback_query.from_user.id, "Отлично, подписка подтверждена ✨ Начинаем курс!")
        await send_lesson(callback_query.from_user.id, 1)
    else:
        await bot.send_message(callback_query.from_user.id, "Пока не вижу подписки 🤔 Проверь ещё раз.")

# ---------------- УРОКИ ----------------
async def send_lesson(user_id, lesson_id):
    lesson = lessons.get(lesson_id)
    if lesson:
        await bot.send_message(user_id, lesson["text"])
    else:
        await bot.send_message(user_id, "Курс завершён 🎉 Напиши /answers, чтобы посмотреть свои ответы.")

# ---------------- ЗАПУСК ----------------
if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_db())
    executor.start_polling(dp, skip_updates=True)
