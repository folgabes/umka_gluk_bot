import os
import json
from aiogram import Bot, Dispatcher, executor, types
import asyncpg

API_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

CHANNEL_USERNAME = "@merkulyevy_live_evolution_space"

# список айдишников админов
ADMINS = [123456789, 987654321]  # сюда вставь свои реальные id

# ---------- Postgres ----------

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
        await conn.execute(
            "INSERT INTO users (id, answers, current) VALUES ($1, '{}'::jsonb, 1)", user_id
        )
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
            await conn.execute(
                f"UPDATE users SET {key}=$1 WHERE id=$2",
                value,
                user_id,
            )
    await conn.close()

# ---------- Экспорт ----------

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

    # отправляем как файл
    file = types.InputFile.from_buffer(
        text.encode("utf-8"), filename="export.json"
    )
    await message.answer_document(file, caption="📤 Данные выгружены")

# ---------- Остальное (уроки, логика и т.д.) ----------
# ... тут у тебя остаётся то, что мы писали выше

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
