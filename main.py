import os
import json
from aiogram import Bot, Dispatcher, executor, types
import asyncpg

API_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

CHANNEL_USERNAME = "@merkulyevy_live_evolution_space"

# список айдишников админов
ADMINS = [123456789, 987654321]  # замени на реальные id

# ----------- уроки -----------
lessons = {
    1: {
        "question": "Вспомни, пожалуйста, какие преодолённые тобой трудности укрепили твоё здоровье и помогли обрести внутреннюю силу и спокойствие?",
        "text": "📽 Урок 1. Здоровье можно поменять на деньги\n\nПосмотри видео:\n"
                "🔗 [Rutube](https://rutube.ru/video/private/438c67c0e3510477ba92ef1c9cbda807/?p=m8ZK3IF63nq3U8aiuKBfyQ)\n"
                "🔗 [YouTube](https://youtube.com/shorts/_uTHQopErp4)\n\n"
                "📝 Задание:\nВспомни, пожалуйста, какие преодолённые тобой трудности укрепили твоё здоровье и помогли обрести внутреннюю силу и спокойствие?"
    },
    2: {
        "question": "Расскажи о моментах в своей жизни, когда деньги принесли тебе настоящее счастье и радость. Были ли эпизоды, когда обладание ими стало источником огорчений и переживаний?",
        "text": "📽 Урок 2. Деньги могут спасти от старости и смерти\n\nПосмотри видео:\n"
                "🔗 [Rutube](https://rutube.ru/video/private/a455fedbc14d98eeac76e09dec70aaa8/?p=O-rFwwAB4tvSNHOJK5gDgw)\n"
                "🔗 [YouTube](https://youtube.com/shorts/6KOFfzMXeBo)\n\n"
                "📝 Задание:\nРасскажи о моментах в своей жизни, когда деньги принесли тебе настоящее счастье и радость. "
                "Были ли эпизоды, когда обладание ими стало источником огорчений и переживаний?"
    },
    3: {
        "question": "Поделись историей о том, как ты распорядился(ась) случайно обретёнными средствами. Какой полезный вывод ты сделал(а) из этого опыта?",
        "text": "📽 Урок 3. Лёгкие деньги легко даются\n\nПосмотри видео:\n"
                "🔗 [Rutube](https://rutube.ru/video/private/ad9e2b3c210d21cd23712045627dab40/?p=Ib29o4dCFybWBwITaw8EcA)\n"
                "🔗 [YouTube](https://youtube.com/shorts/nzpJTNZseH8)\n\n"
                "📝 Задание:\nПоделись историей о том, как ты распорядился(ась) случайно обретёнными средствами. "
                "Какой полезный вывод ты сделал(а) из этого опыта?"
    },
    4: {
        "question": "Какие действия, на твой взгляд, уберегут тебя от потери денег и помогут защитить средства при хранении?",
        "text": "📽 Урок 4. Деньги можно сохранить без риска потерять\n\nПосмотри видео:\n"
                "🔗 [Rutube](https://rutube.ru/video/private/17cda71a3427edf4f8210bff14862bcd/?p=mC_3osWPMwJgbZ1mICPjOQ)\n"
                "🔗 [YouTube](https://youtube.com/shorts/nzpJTNZseH8)\n\n"
                "📝 Задание:\nКакие действия, на твой взгляд, уберегут тебя от потери денег и помогут защитить средства при хранении?"
    },
    5: {
        "question": "Какие ценности и возможности остаются доступными человеку, если у него временно отсутствуют деньги?",
        "text": "📽 Урок 5. Купи сейчас, заплатишь потом\n\nПосмотри видео:\n"
                "🔗 [Rutube](https://rutube.ru/video/private/c190ba709164a4e7fe3f0c6be9ffd5d9/?p=OSf95L2cKiR_FfNmC9xzrg)\n"
                "🔗 [YouTube](https://youtube.com/shorts/wkbbH1NzmdY)\n\n"
                "📝 Задание:\nКакие ценности и возможности остаются доступными человеку, если у него временно отсутствуют деньги?"
    },
}

# ----------- база Postgres -----------

async def init_db():
    conn = await asyncpg.connect(
        host=os.getenv("PGHOST"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD"),
        database=os.getenv("PGDATABASE"),
        port=os.getenv("PGPORT"),
    )
    await conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id BIGINT PRIMARY KEY,
        name TEXT,
        email TEXT,
        gender TEXT,
        age_group TEXT,
        sphere TEXT,
        answers JSONB DEFAULT '{}'::jsonb,
        current INT DEFAULT 1
    )
    """)
    await conn.close()

async def get_user(user_id):
    conn = await asyncpg.connect(
        host=os.getenv("PGHOST"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD"),
        database=os.getenv("PGDATABASE"),
        port=os.getenv("PGPORT"),
    )
    row = await conn.fetchrow("SELECT * FROM users WHERE id=$1", user_id)
    if not row:
        await conn.execute("INSERT INTO users (id, answers, current) VALUES ($1, '{}'::jsonb, 1)", user_id)
        row = await conn.fetchrow("SELECT * FROM users WHERE id=$1", user_id)
    await conn.close()
    return dict(row)

async def update_user(user_id, **kwargs):
    conn = await asyncpg.connect(
        host=os.getenv("PGHOST"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD"),
        database=os.getenv("PGDATABASE"),
        port=os.getenv("PGPORT"),
    )
    for key, value in kwargs.items():
        if key == "answers" and value is not None:
            await conn.execute(
                "UPDATE users SET answers = answers || $1::jsonb WHERE id=$2",
                json.dumps(value),
                user_id,
            )
        else:
            await conn.execute(f"UPDATE users SET {key}=$1 WHERE id=$2", value, user_id)
    await conn.close()

# ----------- экспорт -----------

@dp.message_handler(commands=["export"])
async def export_data(message: types.Message):
    if message.from_user.id not in ADMINS:
        await message.answer("⛔ У тебя нет прав на экспорт.")
        return
    conn = await asyncpg.connect(
        host=os.getenv("PGHOST"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD"),
        database=os.getenv("PGDATABASE"),
        port=os.getenv("PGPORT"),
    )
    rows = await conn.fetch("SELECT * FROM users")
    await conn.close()
    data = [dict(r) for r in rows]
    text = json.dumps(data, ensure_ascii=False, indent=2)
    file = types.InputFile.from_buffer(text.encode("utf-8"), filename="export.json")
    await message.answer_document(file, caption="📤 Данные выгружены")

# ----------- старт и анкета -----------

@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    await init_db()
    await get_user(message.from_user.id)
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton("🚀 Начать"))
    await message.answer("Привет! 👋 Я бот для курса. Нажми кнопку, чтобы начать.", reply_markup=kb)

@dp.message_handler(lambda m: m.text == "🚀 Начать")
async def start_survey(message: types.Message):
    await update_user(message.from_user.id, current=0)
    await message.answer("Как тебя зовут?")
    await update_user(message.from_user.id, step="ask_name")

@dp.message_handler()
async def handle_message(message: types.Message):
    user = await get_user(message.from_user.id)
    step = user.get("step")

    if step == "ask_name":
        await update_user(message.from_user.id, name=message.text, step="ask_email")
        await message.answer("Укажи свой email:")
    elif step == "ask_email":
        await update_user(message.from_user.id, email=message.text, step="ask_gender")
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add("Мужчина", "Женщина")
        await message.answer("Укажи свой пол:", reply_markup=kb)
    elif step == "ask_gender":
        await update_user(message.from_user.id, gender=message.text, step="ask_age")
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add("до 20", "20-30", "31-45", "46-60", "больше 60")
        await message.answer("Твой возраст?", reply_markup=kb)
    elif step == "ask_age":
        await update_user(message.from_user.id, age_group=message.text, step="ask_sphere")
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add("предприниматель", "свой бизнес", "фрилансер", "руководитель в найме", "сотрудник в найме", "не работаю")
        await message.answer("Выбери сферу деятельности:", reply_markup=kb)
    elif step == "ask_sphere":
        await update_user(message.from_user.id, sphere=message.text, step="lessons", current=1)
        await message.answer("Спасибо! Теперь перейдём к урокам.", reply_markup=types.ReplyKeyboardRemove())
        await message.answer(lessons[1]["text"])
    elif step == "lessons":
        current = user.get("current", 1)
        await update_user(message.from_user.id, answers={str(current): message.text})
        next_lesson = current + 1
        if next_lesson in lessons:
            await update_user(message.from_user.id, current=next_lesson)
            await message.answer(lessons[next_lesson]["text"])
        else:
            await message.answer("🎉 Ты прошёл все уроки! Спасибо за участие.")
            await update_user(message.from_user.id, step="done")

# ----------- запуск -----------

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
