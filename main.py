from aiogram import Bot, Dispatcher, executor, types
import json
import os

API_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

lessons = {
    1: {"text": "Урок 1: приветствие\n\nЧто тебя привело сюда?", "task": "Ответь в свободной форме."},
    2: {"text": "Урок 2: наблюдение\n\nКогда ты впервые подумал(а), что с деньгами что-то не так?", "task": "Поделись воспоминанием."},
    3: {"text": "Урок 3: глюк\n\nОпиши один свой глюк про деньги — стыд, страх, ограничение?", "task": "Что всплыло?"}
}

DATA_FILE = "data.json"
ADMIN_ID = 123456789  # замени на свой user_id

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_user_data(user_id):
    data = load_data()
    user_id = str(user_id)
    return data.get(user_id, {"step": "ask_name", "answers": {}, "current": 1})

def update_user_data(user_id, new_data):
    data = load_data()
    user_id = str(user_id)
    if user_id not in data:
        data[user_id] = {"step": "ask_name", "answers": {}, "current": 1}
    data[user_id].update(new_data)
    save_data(data)

@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    user_id = str(message.from_user.id)
    data = load_data()
    if user_id not in data:
        data[user_id] = {"step": "ask_name", "answers": {}, "current": 1}
        save_data(data)

    await message.answer("👋 Привет! Это бот для курса *Глюки про деньги*.\n\nПеред стартом давай немного познакомимся.")
    await message.answer("Как тебя зовут?")

@dp.message_handler(commands=["reset"])
async def reset_user(message: types.Message):
    data = load_data()
    user_id = str(message.from_user.id)
    if user_id in data:
        del data[user_id]
        save_data(data)
    await message.answer("Прогресс обнулён. Напиши /start, чтобы начать заново.")

@dp.message_handler(commands=["help"])
async def help_user(message: types.Message):
    await bot.send_message(ADMIN_ID, f"🆘 Помощь от @{message.from_user.username} ({message.from_user.id})")
    await message.answer("Запрос отправлен куратору. Мы скоро свяжемся с тобой.")

@dp.message_handler()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    step = user_data.get("step", "ask_name")

    if step == "ask_name":
        update_user_data(user_id, {"name": message.text.strip(), "step": "ask_email"})
        await message.answer("Спасибо! А теперь напиши email, чтобы мы могли прислать тебе материалы после курса")

    elif step == "ask_email":
        update_user_data(user_id, {"email": message.text.strip(), "step": "lesson"})
        await message.answer("Отлично, начинаем ✨")
        await send_lesson(user_id, 1)

    elif step == "lesson":
        current = user_data.get("current", 1)
        if current > len(lessons):
            await message.answer("Курс завершён. Напиши /reset, чтобы начать заново.")
            return
        update_user_data(user_id, {
            "answers": {**user_data.get("answers", {}), str(current): message.text.strip()},
            "current": current + 1
        })
        await send_lesson(user_id, current + 1)

async def send_lesson(user_id, lesson_id):
    lesson = lessons.get(lesson_id)
    if lesson:
        text = f"{lesson['text']}\n\n📝 {lesson['task']}"
        await bot.send_message(user_id, text)
    else:
        await bot.send_message(user_id, "Поздравляю, ты завершил(а) курс! 🎉")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
