import os
import json
import asyncpg
from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

CHANNEL_USERNAME = "@merkulyevy_live_evolution_space"


# ------------------- DB -------------------
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
        current INT DEFAULT 1,
        step TEXT DEFAULT 'ask_name'
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
        await conn.execute("""
            INSERT INTO users (id, answers, current, step) 
            VALUES ($1, '{}'::jsonb, 1, 'ask_name')
        """, user_id)
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


# ------------------- BOT -------------------
@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    user = await get_user(message.from_user.id)

    if user["name"]:  
        # уже есть в базе → продолжаем с того места, где остановился
        await message.answer("Привет! 👋 Рад тебя снова видеть. Продолжим?")
    else:
        # новый пользователь → показываем кнопку только один раз
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add("Начать")
        await message.answer("Привет! 👋 Я бот для курса. Нажми кнопку, чтобы начать.", reply_markup=keyboard)


@dp.message_handler(lambda msg: msg.text == "Начать")
async def start_registration(message: types.Message):
    await update_user(message.from_user.id, step="ask_name")
    # убираем клавиатуру после первого использования
    await message.answer("Как тебя зовут?", reply_markup=types.ReplyKeyboardRemove())


# тут пойдут остальные шаги (имя → email → пол → возраст → сфера → уроки)
# ...


if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_db())
    executor.start_polling(dp, skip_updates=True)
