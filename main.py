import os
import asyncpg
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

API_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

bot = Bot(token=API_TOKEN, parse_mode="MarkdownV2")
dp = Dispatcher(bot)

CHANNEL_USERNAME = "@merkulyevy_live_evolution_space"

# ---------------- УРОКИ ----------------
lessons = {
    1: {
        "question": "Вспомни, пожалуйста, какие преодолённые тобой трудности укрепили твоё здоровье и помогли обрести внутреннюю силу и спокойствие?",
        "text": "📽 Урок 1. Здоровье можно поменять на деньги\n\n🔗 [Rutube](https://rutube.ru/video/private/438c67c0e3510477ba92ef1c9cbda807/?p=m8ZK3IF63nq3U8aiuKBfyQ)\n🔗 [YouTube](https://youtube.com/shorts/_uTHQopErp4)\n\n---\n\n📝 Задание:\n\nВспомни, пожалуйста, какие преодолённые тобой трудности укрепили твоё здоровье и помогли обрести внутреннюю силу и спокойствие?",
    },
    2: {
        "question": "Расскажи о моментах в своей жизни, когда деньги принесли тебе настоящее счастье и радость. Были ли эпизоды, когда обладание ими стало источником огорчений и переживаний?",
        "text": "📽 Урок 2. Деньги могут спасти от старости и смерти\n\n🔗 [Rutube](https://rutube.ru/video/private/a455fedbc14d98eeac76e09dec70aaa8/?p=O-rFwwAB4tvSNHOJK5gDgw)\n🔗 [YouTube](https://youtube.com/shorts/6KOFfzMXeBo)\n\n---\n\n📝 Задание:\n\nРасскажи о моментах в своей жизни, когда деньги принесли тебе настоящее счастье и радость.\n\nБыли ли эпизоды, когда обладание ими стало источником огорчений и переживаний?",
    },
    3: {
        "question": "Поделись историей о том, как ты распорядился(ась) случайно обретёнными средствами. Какой полезный вывод ты сделал(а) из этого опыта?",
        "text": "📽 Урок 3. Легкие деньги легко даются\n\n🔗 [Rutube](https://rutube.ru/video/private/ad9e2b3c210d21cd23712045627dab40/?p=Ib29o4dCFybWBwITaw8EcA)\n🔗 [YouTube](https://youtube.com/shorts/nzpJTNZseH8?feature=share)\n\n---\n\n📝 Задание:\n\nПоделись историей о том, как ты распорядился(ась) случайно обретёнными средствами.\n\nКакой полезный вывод ты сделал(а) из этого опыта?",
    },
    4: {
        "question": "Какие действия, на твой взгляд, уберегут тебя от потери денег и помогут защитить средства при хранении?",
        "text": "📽 Урок 4. Деньги можно сохранить без риска потерять\n\n🔗 [Rutube](https://rutube.ru/video/private/17cda71a3427edf4f8210bff14862bcd/?p=mC_3osWPMwJgbZ1mICPjOQ)\n🔗 [YouTube](https://youtube.com/shorts/nzpJTNZseH8?feature=share)\n\n---\n\n📝 Задание:\n\nКакие действия, на твой взгляд, уберегут тебя от потери денег и помогут защитить средства при хранении?",
    },
    5: {
        "question": "Какие ценности и возможности остаются доступными человеку, если у него временно отсутствуют деньги?",
        "text": "📽 Урок 5. Купи сейчас, заплатишь потом\n\n🔗 [Rutube](https://rutube.ru/video/private/c190ba709164a4e7fe3f0c6be9ffd5d9/?p=OSf95L2cKiR_FfNmC9xzrg)\n🔗 [YouTube](https://youtube.com/shorts/wkbbH1NzmdY)\n\n---\n\n📝 Задание:\n\nКакие ценности и возможности остаются доступными человеку, если у него временно отсутствуют деньги?",
    },
}

# ---------------- ИНИЦИАЛИЗАЦИЯ БД ----------------
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
        current INTEGER
    )
    """)
    await conn.execute("""
    CREATE TABLE IF NOT EXISTS answers (
        id SERIAL PRIMARY KEY,
        user_id BIGINT,
        lesson INTEGER,
        answer TEXT
    )
    """)
    await conn.close()

# ---------------- УТИЛИТЫ ----------------
async def get_user(user_id):
    conn = await asyncpg.connect(DATABASE_URL)
    user = await conn.fetchrow("SELECT * FROM users WHERE user_id=$1", user_id)
    await conn.close()
    return dict(user) if user else None

async def update_user(user_id, **fields):
    conn = await asyncpg.connect(DATABASE_URL)
    user = await conn.fetchrow("SELECT * FROM users WHERE user_id=$1", user_id)
    if user:
        sets = ", ".join([f"{k} = ${i+2}" for i, k in enumerate(fields.keys())])
        await conn.execute(f"UPDATE users SET {sets} WHERE user_id=$1", user_id, *fields.values())
    else:
        columns = ", ".join(["user_id"] + list(fields.keys()))
        placeholders = ", ".join([f"${i+1}" for i in range(len(fields) + 1)])
        await conn.execute(f"INSERT INTO users ({columns}) VALUES ({placeholders})", user_id, *([*fields.values()]))
    await conn.close()

async def save_answer(user_id, lesson, answer):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("INSERT INTO answers (user_id, lesson, answer) VALUES ($1, $2, $3)", user_id, lesson, answer)
    await conn.close()

async def get_answers(user_id):
    conn = await asyncpg.connect(DATABASE_URL)
    rows = await conn.fetch("SELECT lesson, answer FROM answers WHERE user_id=$1 ORDER BY lesson", user_id)
    await conn.close()
    return rows

async def check_subscription(user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ---------------- СТАРТ ----------------
@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Начать", callback_data="start_course"))
    await message.answer("Привет! 👋 Я бот для курса. Нажми кнопку, чтобы начать.", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == "start_course")
async def process_start(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    await update_user(user_id, step="ask_name", current=1)
    await bot.send_message(user_id, "Как тебя зовут?")

# ---------------- АНКЕТА ----------------
@dp.message_handler()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    user = await get_user(user_id)
    if not user:
        return

    step = user.get("step")

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
            await message.answer("Отлично, ты уже подписан ✨ Начинаем курс!")
            await send_lesson(user_id, 1)
        else:
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("🔔 Подписаться на канал", url="https://t.me/merkulyevy_live_evolution_space"))
            keyboard.add(InlineKeyboardButton("✅ Я подписался", callback_data="check_subscription"))
            await message.answer("⚠️ Чтобы пройти курс, нужно быть подписанным на наш канал.\n\nПодпишись и нажми «Я подписался».", reply_markup=keyboard)

    elif step == "lesson":
        current = user.get("current", 1)
        await save_answer(user_id, current, message.text.strip())
        next_lesson = current + 1
        await update_user(user_id, current=next_lesson)
        await send_lesson(user_id, next_lesson)

# ---------------- ПОДПИСКА ----------------
@dp.callback_query_handler(lambda c: c.data == "check_subscription")
async def process_subscription(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    if await check_subscription(user_id):
        await update_user(user_id, step="lesson", current=1)
        await bot.send_message(user_id, "Отлично, подписка подтверждена ✨ Начинаем курс!")
        await send_lesson(user_id, 1)
    else:
        await bot.send_message(user_id, "Пока не вижу подписки 🤔 Проверь ещё раз и нажми «Я подписался».")

# ---------------- УРОКИ ----------------
async def send_lesson(user_id, lesson_id):
    if lesson_id > len(lessons):
        await bot.send_message(user_id, "Курс завершён 🎉\n\nНапиши /answers, чтобы посмотреть свои ответы.")
        return
    lesson = lessons[lesson_id]
    await bot.send_message(user_id, lesson["text"])

# ---------------- КОМАНДЫ ----------------
@dp.message_handler(commands=["answers"])
async def answers_cmd(message: types.Message):
    rows = await get_answers(message.from_user.id)
    if not rows:
        await message.answer("У тебя пока нет сохранённых ответов ✍️")
        return
    text = "📒 Твои ответы по курсу:\n\n"
    for row in rows:
        lesson_id, answer = row["lesson"], row["answer"]
        question = lessons[lesson_id]["question"]
        text += f"📽 Урок {lesson_id}. {question}\nОтвет: {answer}\n\n"
    await message.answer(text)

# ---------------- ЗАПУСК ----------------
if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_db())
    executor.start_polling(dp, skip_updates=True)
