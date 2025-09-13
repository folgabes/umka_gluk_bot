from aiogram import Bot, Dispatcher, executor, types
import json
import os

API_TOKEN = os.getenv("BOT_TOKEN")  # вставь токен в переменные окружения на Railway
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

lessons = {
    1: {"text": "Урок 1: приветствие\n\nЧто тебя привело сюда?", "task": "Ответь в свободной форме."},
    2: {"text": "Урок 2: наблюдение\n\nКогда ты впервые подумал(а), что с деньгами что-то не так?", "task": "Поделись воспоминанием."},
    3: {"text": "Урок 3: глюк\n\nОпиши один свой глюк про деньги — стыд, страх, ограничение?", "task": "Что всплыло?"}
    # Добавь остальные уроки по желанию
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

def get_user_progress(user_id):
    data = load_data()
    user_id = str(user_id)
    return data.get(user_id, {"answers": {}, "current": 1})

def update_user_progress(user_id, lesson_id, answer):
    data = load_data()
    user_id = str(user_id)
    if user_id not in data:
        data[user_id] = {"answers": {}, "current": 1}
    data[user_id]["answers"][str(lesson_id)] = answer
    data[user_id]["current"] = lesson_id + 1
    save_data(data)

@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    user = message.from_user
    progress = get_user_progress(user.id)
    current = progress["current"]
    if current > len(lessons):
        await message.answer("Ты уже прошёл(ла) курс. Хочешь пройти заново? /reset")
    else:
        await send_lesson(user.id, current)

async def send_lesson(user_id, lesson_id):
    lesson = lessons.get(lesson_id)
    if lesson:
        text = f"{lesson['text']}\n\n📝 {lesson['task']}"
        await bot.send_message(user_id, text)
    else:
        await bot.send_message(user_id, "Поздравляю, ты завершил(а) курс! 🎉")

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
async def handle_answer(message: types.Message):
    user_id = message.from_user.id
    progress = get_user_progress(user_id)
    current = progress["current"]
    if current > len(lessons):
        await message.answer("Курс завершён. Напиши /reset, чтобы начать заново.")
        return
    update_user_progress(user_id, current, message.text)
    await send_lesson(user_id, current + 1)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
