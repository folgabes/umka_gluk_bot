from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import asyncio
import asyncpg
import os

API_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = "@merkulyevy_live_evolution_space"

# подключение к Postgres
async def create_pool():
    return await asyncpg.create_pool(
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD"),
        database=os.getenv("PGDATABASE"),
        host=os.getenv("PGHOST"),
        port=os.getenv("PGPORT"),
    )

pool = None

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

lessons = {
    1: {
        "question": "Вспомни, пожалуйста, какие преодолённые тобой трудности укрепили твоё здоровье и помогли обрести внутреннюю силу и спокойствие?",
        "text": "📽 Урок 1. Здоровье можно поменять на деньги\n\nПосмотри видео:\nhttps://rutube.ru/video/private/438c67c0e3510477ba92ef1c9cbda807/?p=m8ZK3IF63nq3U8aiuKBfyQ\nhttps://youtube.com/shorts/_uTHQopErp4\n\n---\n\n📝 Задание:\n\nВспомни, пожалуйста, какие преодолённые тобой трудности укрепили твоё здоровье и помогли обрести внутреннюю силу и спокойствие?",
    },
    2: {
        "question": "Расскажи о моментах в своей жизни, когда деньги принесли тебе настоящее счастье и радость. Были ли эпизоды, когда обладание ими стало источником огорчений и переживаний?",
        "text": "📽 Урок 2. Деньги могут спасти от старости и смерти\n\nПосмотри видео:\nhttps://rutube.ru/video/private/a455fedbc14d98eeac76e09dec70aaa8/?p=O-rFwwAB4tvSNHOJK5gDgw\nhttps://youtube.com/shorts/6KOFfzMXeBo\n\n---\n\n📝 Задание:\n\nРасскажи о моментах в своей жизни, когда деньги принесли тебе настоящее счастье и радость.\nБыли ли эпизоды, когда обладание ими стало источником огорчений и переживаний?",
    },
    3: {
        "question": "Поделись историей о том, как ты распорядился(ась) случайно обретёнными средствами. Какой полезный вывод ты сделал(а) из этого опыта?",
        "text": "📽 Урок 3. Легкие деньги легко даются\n\nПосмотри видео:\nhttps://rutube.ru/video/private/ad9e2b3c210d21cd23712045627dab40/?p=Ib29o4dCFybWBwITaw8EcA\nhttps://youtube.com/shorts/nzpJTNZseH8?feature=share\n\n---\n\n📝 Задание:\n\nПоделись историей о том, как ты распорядился(ась) случайно обретёнными средствами.\nКакой полезный вывод ты сделал(а) из этого опыта?",
    },
    4: {
        "question": "Какие действия, на твой взгляд, уберегут тебя от потери денег и помогут защитить средства при хранении?",
        "text": "📽 Урок 4. Деньги можно сохранить без риска потерять\n\nПосмотри видео:\nhttps://rutube.ru/video/private/17cda71a3427edf4f8210bff14862bcd/?p=mC_3osWPMwJgbZ1mICPjOQ\nhttps://youtube.com/shorts/nzpJTNZseH8?feature=share\n\n---\n\n📝 Задание:\n\nКакие действия, на твой взгляд, уберегут тебя от потери денег и помогут защитить средства при хранении?",
    },
    5: {
        "question": "Какие ценности и возможности остаются доступными человеку, если у него временно отсутствуют деньги?",
        "text": "📽 Урок 5. Купи сейчас, заплатишь потом\n\nПосмотри видео:\nhttps://rutube.ru/video/private/c190ba709164a4e7fe3f0c6be9ffd5d9/?p=OSf95L2cKiR_FfNmC9xzrg\nhttps://youtube.com/shorts/wkbbH1NzmdY\n\n---\n\n📝 Задание:\n\nКакие ценности и возможности остаются доступными человеку, если у него временно отсутствуют деньги?",
    },
}

# храним временные шаги пользователя в памяти
user_steps = {}

async def check_subscription(user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# старт
@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add("Начать")
    user_steps[message.from_user.id] = "start"
    await message.answer("Привет! 👋 Я бот для курса. Нажми кнопку, чтобы начать.", reply_markup=kb)

# обработка кнопки Начать
@dp.message_handler(lambda m: m.text == "Начать")
async def handle_start_button(message: types.Message):
    user_steps[message.from_user.id] = "ask_name"
    await message.answer("Как тебя зовут?", reply_markup=types.ReplyKeyboardRemove())

# последовательные шаги анкеты
@dp.message_handler()
async def process(message: types.Message):
    user_id = message.from_user.id
    step = user_steps.get(user_id)

    if step == "ask_name":
        user_steps[user_id] = "ask_email"
        await message.answer("Укажи, пожалуйста, свой email:")

    elif step == "ask_email":
        user_steps[user_id] = "ask_gender"
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        kb.add("Мужчина", "Женщина")
        await message.answer("Ты мужчина или женщина?", reply_markup=kb)

    elif step == "ask_gender":
        user_steps[user_id] = "ask_age"
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        kb.add("до 20", "20-30", "31-45", "46-60", "больше 60")
        await message.answer("Укажи свой возраст:", reply_markup=kb)

    elif step == "ask_age":
        user_steps[user_id] = "ask_field"
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        kb.add("предприниматель", "свой бизнес", "фрилансер", "руководитель в найме", "сотрудник в найме", "не работаю")
        await message.answer("Выбери сферу деятельности:", reply_markup=kb)

    elif step == "ask_field":
        user_steps[user_id] = "check_sub"
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        kb.add("Готово")
        await message.answer(
            "Спасибо! Теперь нужно подписаться на канал 👉 https://t.me/merkulyevy_live_evolution_space\n\n"
            "Когда подпишешься — нажми кнопку «Готово».",
            reply_markup=kb
        )

    elif step == "check_sub":
        if message.text == "Готово":
            if await check_subscription(user_id):
                user_steps[user_id] = "lesson_1"
                await message.answer(lessons[1]["text"], reply_markup=types.ReplyKeyboardRemove())
            else:
                await message.answer("❗️ Я не вижу подписки. Подпишись на канал и снова нажми «Готово».")
        else:
            await message.answer("Нажми кнопку «Готово», когда подпишешься.")

    elif step and step.startswith("lesson_"):
        num = int(step.split("_")[1])
        # тут сохраняем ответ в базу
        async with pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO answers(user_id, lesson, answer) VALUES($1, $2, $3) "
                "ON CONFLICT (user_id, lesson) DO UPDATE SET answer=$3",
                user_id, num, message.text
            )
        if num < len(lessons):
            user_steps[user_id] = f"lesson_{num+1}"
            await message.answer(lessons[num+1]["text"])
        else:
            user_steps[user_id] = "done"
            await message.answer("🎉 Спасибо! Ты прошёл все уроки.")

# экспорт только для админов
ADMINS = [123456789, 987654321]  # сюда подставь id
@dp.message_handler(commands=["export"])
async def export_answers(message: types.Message):
    if message.from_user.id not in ADMINS:
        await message.answer("У тебя нет прав для этой команды.")
        return
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT user_id, lesson, answer FROM answers ORDER BY user_id, lesson")
    text = "📒 Все ответы:\n\n"
    for r in rows:
        text += f"👤 {r['user_id']} | Урок {r['lesson']} | {r['answer']}\n"
    await message.answer(text or "Нет данных.")

# создаём таблицу в Postgres
async def on_startup(dp):
    global pool
    pool = await create_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS answers (
            user_id BIGINT,
            lesson INT,
            answer TEXT,
            PRIMARY KEY (user_id, lesson)
        )
        """)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(on_startup(dp))
    executor.start_polling(dp, skip_updates=True)
