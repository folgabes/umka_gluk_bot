import os
import io
import csv
import asyncpg
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# ---------- config ----------
API_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = "@merkulyevy_live_evolution_space"

# админы: можно задать переменной окружения ADMIN_IDS="123,456" или править список ниже
ADMIN_IDS = [
    int(x) for x in (os.getenv("ADMIN_IDS", "").split(",") if os.getenv("ADMIN_IDS") else [])
] or [111111111, 222222222]  # <-- замените на ваши реальные id

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

pool: asyncpg.Pool = None  # postgres pool

# ---------- lessons ----------
lessons = {
    1: {
        "question": "Вспомни, пожалуйста, какие преодолённые тобой трудности укрепили твоё здоровье и помогли обрести внутреннюю силу и спокойствие?",
        "text": (
            "📽 Урок 1. Здоровье можно поменять на деньги\n\n"
            "Посмотри видео:\n"
            "🔗 Rutube: https://rutube.ru/video/private/438c67c0e3510477ba92ef1c9cbda807/?p=m8ZK3IF63nq3U8aiuKBfyQ\n"
            "🔗 YouTube: https://youtube.com/shorts/_uTHQopErp4\n\n"
            "— — —\n\n"
            "📝 Задание:\n"
            "Вспомни, пожалуйста, какие преодолённые тобой трудности укрепили твоё здоровье и помогли обрести внутреннюю силу и спокойствие?"
        ),
    },
    2: {
        "question": "Расскажи о моментах в своей жизни, когда деньги принесли тебе настоящее счастье и радость. Были ли эпизоды, когда обладание ими стало источником огорчений и переживаний?",
        "text": (
            "📽 Урок 2. Деньги могут спасти от старости и смерти\n\n"
            "Посмотри видео:\n"
            "🔗 Rutube: https://rutube.ru/video/private/a455fedbc14d98eeac76e09dec70aaa8/?p=O-rFwwAB4tvSNHOJK5gDgw\n"
            "🔗 YouTube: https://youtube.com/shorts/6KOFfzMXeBo\n\n"
            "— — —\n\n"
            "📝 Задание:\n"
            "Расскажи о моментах в своей жизни, когда деньги принесли тебе настоящее счастье и радость.\n"
            "Были ли эпизоды, когда обладание ими стало источником огорчений и переживаний?"
        ),
    },
    3: {
        "question": "Поделись историей о том, как ты распорядился(ась) случайно обретёнными средствами. Какой полезный вывод ты сделал(а) из этого опыта?",
        "text": (
            "📽 Урок 3. Легкие деньги легко даются\n\n"
            "Посмотри видео:\n"
            "🔗 Rutube: https://rutube.ru/video/private/ad9e2b3c210d21cd23712045627dab40/?p=Ib29o4dCFybWBwITaw8EcA\n"
            "🔗 YouTube: https://youtube.com/shorts/nzpJTNZseH8\n\n"
            "— — —\n\n"
            "📝 Задание:\n"
            "Поделись историей о том, как ты распорядился(ась) случайно обретёнными средствами.\n"
            "Какой полезный вывод ты сделал(а) из этого опыта?"
        ),
    },
    4: {
        "question": "Какие действия, на твой взгляд, уберегут тебя от потери денег и помогут защитить средства при хранении?",
        "text": (
            "📽 Урок 4. Деньги можно сохранить без риска потерять\n\n"
            "Посмотри видео:\n"
            "🔗 Rutube: https://rutube.ru/video/private/17cda71a3427edf4f8210bff14862bcd/?p=mC_3osWPMwJgbZ1mICPjOQ\n"
            "🔗 YouTube: https://youtube.com/shorts/nzpJTNZseH8\n\n"
            "— — —\n\n"
            "📝 Задание:\n"
            "Какие действия, на твой взгляд, уберегут тебя от потери денег и помогут защитить средства при хранении?"
        ),
    },
    5: {
        "question": "Какие ценности и возможности остаются доступными человеку, если у него временно отсутствуют деньги?",
        "text": (
            "📽 Урок 5. Купи сейчас, заплатишь потом\n\n"
            "Посмотри видео:\n"
            "🔗 Rutube: https://rutube.ru/video/private/c190ba709164a4e7fe3f0c6be9ffd5d9/?p=OSf95L2cKiR_FfNmC9xzrg\n"
            "🔗 YouTube: https://youtube.com/shorts/wkbbH1NzmdY\n\n"
            "— — —\n\n"
            "📝 Задание:\n"
            "Какие ценности и возможности остаются доступными человеку, если у него временно отсутствуют деньги?"
        ),
    },
}

# ---------- DB helpers ----------
async def init_db():
    async with pool.acquire() as conn:
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id        BIGINT PRIMARY KEY,
            name      TEXT,
            email     TEXT,
            gender    TEXT,
            age_group TEXT,
            work_area TEXT,
            step      TEXT NOT NULL DEFAULT 'start',
            current   INT  NOT NULL DEFAULT 1
        );
        """)
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS answers (
            user_id    BIGINT REFERENCES users(id) ON DELETE CASCADE,
            lesson_num INT,
            answer     TEXT,
            PRIMARY KEY (user_id, lesson_num)
        );
        """)

async def get_user(user_id: int) -> dict:
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM users WHERE id=$1", user_id)
        if not row:
            await conn.execute(
                "INSERT INTO users(id) VALUES($1) ON CONFLICT DO NOTHING", user_id
            )
            row = await conn.fetchrow("SELECT * FROM users WHERE id=$1", user_id)
        return dict(row)

async def update_user(user_id: int, **fields):
    if not fields:
        return
    cols, vals = [], []
    for i, (k, v) in enumerate(fields.items(), start=1):
        cols.append(f"{k} = ${i}")
        vals.append(v)
    vals.append(user_id)
    sql = f"UPDATE users SET {', '.join(cols)} WHERE id = ${len(vals)}"
    async with pool.acquire() as conn:
        await conn.execute(sql, *vals)

async def save_answer(user_id: int, lesson_num: int, answer: str):
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO answers(user_id, lesson_num, answer)
            VALUES($1,$2,$3)
            ON CONFLICT (user_id, lesson_num) DO UPDATE SET answer=EXCLUDED.answer
            """,
            user_id, lesson_num, answer
        )

async def get_answers(user_id: int) -> dict:
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT lesson_num, answer FROM answers WHERE user_id=$1 ORDER BY lesson_num", user_id
        )
        return {str(r["lesson_num"]): r["answer"] for r in rows}

async def reset_user(user_id: int):
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM answers WHERE user_id=$1", user_id)
        await conn.execute("UPDATE users SET step='start', current=1 WHERE id=$1", user_id)

# ---------- utils ----------
async def check_subscription(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ("member", "administrator", "creator")
    except Exception:
        return False

def start_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(types.KeyboardButton("Начать"))
    return kb

def gender_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add("Мужчина", "Женщина")
    return kb

def age_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add("до 20", "20-30", "31-45", "46-60", "больше 60")
    return kb

def work_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.row("предприниматель", "свой бизнес", "фрилансер")
    kb.row("руководитель в найме", "сотрудник в найме", "не работаю")
    return kb

def done_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add("Готово")
    return kb

# ---------- handlers ----------
@dp.message_handler(commands=["start"])
async def cmd_start(m: types.Message):
    user = await get_user(m.from_user.id)
    if user["step"] == "start":
        await m.answer("привет! 👋 я бот курса «глюки про деньги». нажми кнопку, чтобы начать.", reply_markup=start_kb())
    else:
        # продолжим с того места, где человек остановился
        await continue_flow(m, user)

@dp.message_handler(commands=["reset"])
async def cmd_reset(m: types.Message):
    await reset_user(m.from_user.id)
    await m.answer("ок, всё обнулила. жми «Начать».", reply_markup=start_kb())

@dp.message_handler(commands=["answers"])
async def cmd_answers(m: types.Message):
    answers = await get_answers(m.from_user.id)
    if not answers:
        await m.answer("пока нет сохранённых ответов ✍️")
        return
    text = "📒 твои ответы по курсу:\n\n"
    for num in sorted(answers, key=lambda x: int(x)):
        q = lessons[int(num)]["question"]
        text += f"📽 урок {num}. {q}\nответ: {answers[num]}\n\n"
    await m.answer(text)

@dp.message_handler(commands=["export"])
async def cmd_export(m: types.Message):
    if m.from_user.id not in ADMIN_IDS:
        await m.answer("⛔ доступ только для админов.")
        return
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT u.id, u.name, u.email, u.gender, u.age_group, u.work_area, a.lesson_num, a.answer
            FROM users u
            LEFT JOIN answers a ON a.user_id = u.id
            ORDER BY u.id, a.lesson_num
        """)
    # делаем CSV
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["user_id","name","email","gender","age","work_area","lesson","answer"])
    for r in rows:
        w.writerow([r["id"], r["name"], r["email"], r["gender"], r["age_group"], r["work_area"], r["lesson_num"], r["answer"]])
    buf.seek(0)
    await m.answer_document(types.InputFile(buf, filename="export.csv"))

@dp.message_handler(lambda m: m.text == "Начать")
async def btn_start(m: types.Message):
    await update_user(m.from_user.id, step="ask_name")
    await m.answer("как тебя зовут?", reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler()
async def any_text(m: types.Message):
    user = await get_user(m.from_user.id)
    step = user["step"]

    if step == "ask_name":
        await update_user(m.from_user.id, name=m.text.strip(), step="ask_email")
        await m.answer("укажи свой email:")

    elif step == "ask_email":
        await update_user(m.from_user.id, email=m.text.strip(), step="ask_gender")
        await m.answer("ты мужчина или женщина?", reply_markup=gender_kb())

    elif step == "ask_gender":
        await update_user(m.from_user.id, gender=m.text.strip(), step="ask_age")
        await m.answer("твой возраст:", reply_markup=age_kb())

    elif step == "ask_age":
        await update_user(m.from_user.id, age_group=m.text.strip(), step="ask_work")
        await m.answer("выбери сферу деятельности:", reply_markup=work_kb())

    elif step == "ask_work":
        await update_user(m.from_user.id, work_area=m.text.strip(), step="check_sub")
        await m.answer(
            "спасибо! теперь подпишись на канал:\n"
            "https://t.me/merkulyevy_live_evolution_space\n\n"
            "как подпишешься — жми «Готово».",
            reply_markup=done_kb()
        )

    elif step == "check_sub":
        if m.text == "Готово":
            if await check_subscription(m.from_user.id):
                await update_user(m.from_user.id, step="lesson", current=1)
                await m.answer("подписка подтверждена ✨ начинаем курс!", reply_markup=types.ReplyKeyboardRemove())
                await m.answer(lessons[1]["text"])
            else:
                await m.answer("я пока не вижу подписки 🤔 подпишись и нажми «Готово» ещё раз.")
        else:
            await m.answer("нажми «Готово», когда подпишешься 🙌")

    elif step == "lesson":
        cur = user["current"]
        await save_answer(m.from_user.id, cur, m.text.strip())
        next_id = cur + 1
        if next_id in lessons:
            await update_user(m.from_user.id, current=next_id)
            await m.answer(lessons[next_id]["text"])
        else:
            await update_user(m.from_user.id, step="done")
            await m.answer("🎉 курс завершён! напиши /answers, чтобы посмотреть свои ответы.")

    elif step == "done":
        await m.answer("курс уже пройден. можешь посмотреть /answers или /reset чтобы начать заново.")

    else:
        # если что-то непредвиденное — начнём сначала
        await update_user(m.from_user.id, step="start")
        await m.answer("давай начнём сначала 🙂", reply_markup=start_kb())

async def continue_flow(m: types.Message, user: dict):
    """Если человек вернулся не с 'start' — продолжаем сценарий без лишних кнопок."""
    step = user["step"]
    prompts = {
        "ask_name": "как тебя зовут?",
        "ask_email": "укажи свой email:",
        "ask_gender": "ты мужчина или женщина?",
        "ask_age": "твой возраст:",
        "ask_work": "выбери сферу деятельности:",
        "check_sub": "подпишись на канал и нажми «Готово»: https://t.me/merkulyevy_live_evolution_space",
        "lesson": lessons[user.get("current", 1)]["text"] if user.get("current", 1) in lessons else "продолжим?",
        "done": "курс завершён. /answers покажет твои ответы.",
    }
    reply = prompts.get(step, "продолжим?")
    await m.answer(reply)

# ---------- startup ----------
async def on_startup(_):
    global pool
    pool = await asyncpg.create_pool(
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD"),
        database=os.getenv("PGDATABASE"),
        host=os.getenv("PGHOST"),
        port=os.getenv("PGPORT"),
        min_size=1, max_size=5,
    )
    await init_db()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
