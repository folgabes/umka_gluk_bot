import os
import asyncpg
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

API_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")  # railway даёт эту переменную

bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

CHANNEL_USERNAME = "@merkulyevy_live_evolution_space"

# ---------- УРОКИ ----------
lessons = {
    1: {
        "question": "Вспомни, пожалуйста, какие преодолённые тобой трудности укрепили твоё здоровье и помогли обрести внутреннюю силу и спокойствие?",
        "text": "📽 Урок 1. Здоровье можно поменять на деньги\n\nПосмотри видео:\n🔗 <a href='https://rutube.ru/video/private/438c67c0e3510477ba92ef1c9cbda807/?p=m8ZK3IF63nq3U8aiuKBfyQ'>Rutube</a>\n🔗 <a href='https://youtube.com/shorts/_uTHQopErp4'>YouTube</a>\n\n---\n\n📝 Задание:\nВспомни, пожалуйста, какие преодолённые тобой трудности укрепили твоё здоровье и помогли обрести внутреннюю силу и спокойствие?",
    },
    2: {
        "question": "Расскажи о моментах в своей жизни, когда деньги принесли тебе настоящее счастье и радость. Были ли эпизоды, когда обладание ими стало источником огорчений и переживаний?",
        "text": "📽 Урок 2. Деньги могут спасти от старости и смерти\n\nПосмотри видео:\n🔗 <a href='https://rutube.ru/video/private/a455fedbc14d98eeac76e09dec70aaa8/?p=O-rFwwAB4tvSNHOJK5gDgw'>Rutube</a>\n🔗 <a href='https://youtube.com/shorts/6KOFfzMXeBo'>YouTube</a>\n\n---\n\n📝 Задание:\nРасскажи о моментах в своей жизни, когда деньги принесли тебе настоящее счастье и радость.\nБыли ли эпизоды, когда обладание ими стало источником огорчений и переживаний?",
    },
    3: {
        "question": "Поделись историей о том, как ты распорядился(ась) случайно обретёнными средствами. Какой полезный вывод ты сделал(а) из этого опыта?",
        "text": "📽 Урок 3. Легкие деньги легко даются\n\nПосмотри видео:\n🔗 <a href='https://rutube.ru/video/private/ad9e2b3c210d21cd23712045627dab40/?p=Ib29o4dCFybWBwITaw8EcA'>Rutube</a>\n🔗 <a href='https://youtube.com/shorts/nzpJTNZseH8?feature=share'>YouTube</a>\n\n---\n\n📝 Задание:\nПоделись историей о том, как ты распорядился(ась) случайно обретёнными средствами.\nКакой полезный вывод ты сделал(а) из этого опыта?",
    },
    4: {
        "question": "Какие действия, на твой взгляд, уберегут тебя от потери денег и помогут защитить средства при хранении?",
        "text": "📽 Урок 4. Деньги можно сохранить без риска потерять\n\nПосмотри видео:\n🔗 <a href='https://rutube.ru/video/private/17cda71a3427edf4f8210bff14862bcd/?p=mC_3osWPMwJgbZ1mICPjOQ'>Rutube</a>\n🔗 <a href='https://youtube.com/shorts/nzpJTNZseH8?feature=share'>YouTube</a>\n\n---\n\n📝 Задание:\nКакие действия, на твой взгляд, уберегут тебя от потери денег и помогут защитить средства при хранении?",
    },
    5: {
        "question": "Какие ценности и возможности остаются доступными человеку, если у него временно отсутствуют деньги?",
        "text": "📽 Урок 5. Купи сейчас, заплатишь потом\n\nПосмотри видео:\n🔗 <a href='https://rutube.ru/video/private/c190ba709164a4e7fe3f0c6be9ffd5d9/?p=OSf95L2cKiR_FfNmC9xzrg'>Rutube</a>\n🔗 <a href='https://youtube.com/shorts/wkbbH1NzmdY'>YouTube</a>\n\n---\n\n📝 Задание:\nКакие ценности и возможности остаются доступными человеку, если у него временно отсутствуют деньги?",
    },
}

# ---------- ПОДКЛЮЧЕНИЕ К БД ----------
async def create_db():
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
    )
    """)
    await conn.execute("""
    CREATE TABLE IF NOT EXISTS answers (
        user_id BIGINT,
        lesson INT,
        answer TEXT,
        PRIMARY KEY (user_id, lesson)
    )
    """)
    await conn.close()

# ---------- УТИЛИТЫ ----------
async def get_user(user_id):
    conn = await asyncpg.connect(DATABASE_URL)
    row = await conn.fetchrow("SELECT * FROM users WHERE user_id=$1", user_id)
    await conn.close()
    return row

async def update_user(user_id, **kwargs):
    conn = await asyncpg.connect(DATABASE_URL)
    cols = ", ".join([f"{k}=${i+2}" for i, k in enumerate(kwargs.keys())])
    values = list(kwargs.values())
    await conn.execute(f"""
        INSERT INTO users (user_id, {', '.join(kwargs.keys())})
        VALUES ($1, {', '.join([f'${i+2}' for i in range(len(values))])})
        ON CONFLICT (user_id) DO UPDATE SET {cols}
    """, user_id, *values)
    await conn.close()

async def save_answer(user_id, lesson, answer):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("""
        INSERT INTO answers (user_id, lesson, answer)
        VALUES ($1, $2, $3)
        ON CONFLICT (user_id, lesson) DO UPDATE SET answer=$3
    """, user_id, lesson, answer)
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

# ---------- ХЕНДЛЕРЫ ----------
@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    kb = InlineKeyboardMarkup().add(InlineKeyboardButton("Начать", callback_data="begin"))
    await message.answer("Привет! 👋 Я бот для курса. Нажми кнопку, чтобы начать.", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data == "begin")
async def process_begin(callback: CallbackQuery):
    user_id = callback.from_user.id
    await update_user(user_id, step="ask_name", current=1)
    await bot.send_message(user_id, "Как тебя зовут?")

@dp.message_handler(commands=["answers"])
async def answers_cmd(message: types.Message):
    rows = await get_answers(message.from_user.id)
    if not rows:
        await message.answer("У тебя пока нет сохранённых ответов ✍️")
        return
    text = "📒 Твои ответы по курсу:\n\n"
    for r in rows:
        q = lessons[r["lesson"]]["question"]
        text += f"📽 Урок {r['lesson']}. {q}\nОтвет: {r['answer']}\n\n"
    await message.answer(text)

@dp.message_handler()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    user = await get_user(user_id)
    step = user["step"] if user else "ask_name"

    if step == "ask_name":
        await update_user(user_id, name=message.text.strip(), step="ask_contact")
        await message.answer("Оставь контакт: телефон или ник в Telegram.")
    elif step == "ask_contact":
        await update_user(user_id, contact=message.text.strip(), step="ask_email")
        await message.answer("И последнее — твой email:")
    elif step == "ask_email":
        await update_user(user_id, email=message.text.strip(), step="waiting_subscription")
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("🔔 Подписаться на канал", url="https://t.me/merkulyevy_live_evolution_space"))
        kb.add(InlineKeyboardButton("✅ Я подписался", callback_data="check_subscription"))
        await message.answer("⚠️ Чтобы пройти курс, нужно быть подписанным на наш канал.\n\nПодпишись и нажми «Я подписался».", reply_markup=kb)
    elif step == "lesson":
        current = user["current"]
        await save_answer(user_id, current, message.text.strip())
        next_lesson = current + 1
        await update_user(user_id, current=next_lesson)
        await send_lesson(user_id, next_lesson)

@dp.callback_query_handler(lambda c: c.data == "check_subscription")
async def process_subscription(callback: CallbackQuery):
    user_id = callback.from_user.id
    if await check_subscription(user_id):
        await update_user(user_id, step="lesson", current=1)
        await bot.send_message(user_id, "Отлично, подписка подтверждена ✨ Начинаем курс!")
        await send_lesson(user_id, 1)
    else:
        await bot.send_message(user_id, "Пока не вижу подписки 🤔 Проверь ещё раз и нажми «Я подписался».")

async def send_lesson(user_id, lesson_id):
    if lesson_id in lessons:
        await bot.send_message(user_id, lessons[lesson_id]["text"], disable_web_page_preview=False)
    else:
        await bot.send_message(user_id, "Курс завершён 🎉 Напиши /answers, чтобы посмотреть свои ответы.")

# ---------- ЗАПУСК ----------
if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_db())
    executor.start_polling(dp, skip_updates=True)
