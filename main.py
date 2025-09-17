from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import os, json

API_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=API_TOKEN, parse_mode="Markdown")
dp = Dispatcher(bot)

CHANNEL_USERNAME = "@merkulyevy_live_evolution_space"

# временное хранилище
users = {}

# варианты
gender_options = ["Мужчина", "Женщина"]
age_options = ["до 20", "20-30", "31-45", "46-60", "больше 60"]
work_options = [
    "Предприниматель", "Свой бизнес", "Фрилансер",
    "Руководитель в найме", "Сотрудник в найме",
    "Не работаю по разным причинам"
]

# проверка подписки
async def check_subscription(user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# /start
@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    users[message.from_user.id] = {"step": "ask_name"}
    await message.answer("👋 Привет! Это бот для мини-курса.\n\nКак тебя зовут?")

# /export
@dp.message_handler(commands=["export"])
async def export_cmd(message: types.Message):
    # сохраняем все ответы в файл
    with open("export.json", "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

    await message.answer_document(open("export.json", "rb"))

# обработка текста
@dp.message_handler()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    user = users.get(user_id, {"step": "ask_name"})
    step = user.get("step")

    if step == "ask_name":
        user["name"] = message.text.strip()
        user["step"] = "ask_contact"
        await message.answer("Оставь контакт: телефон или ник в Telegram.")

    elif step == "ask_contact":
        user["contact"] = message.text.strip()
        user["step"] = "ask_gender"
        kb = InlineKeyboardMarkup()
        for g in gender_options:
            kb.add(InlineKeyboardButton(g, callback_data=f"gender:{g}"))
        await message.answer("Вы мужчина или женщина?", reply_markup=kb)

    elif step == "ask_what":
        user["what"] = message.text.strip()
        user["step"] = "waiting_subscription"
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("🔔 Подписаться на канал", url="https://t.me/merkulyevy_live_evolution_space"))
        kb.add(InlineKeyboardButton("✅ Я подписался", callback_data="check_subscription"))
        await message.answer(
            "⚠️ Чтобы пройти курс, нужно быть подписанным на наш канал.\n\nПодпишись и нажми «Я подписался».",
            reply_markup=kb
        )

    users[user_id] = user

# обработка кнопок
@dp.callback_query_handler(lambda c: c.data.startswith("gender:"))
async def process_gender(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    g = callback_query.data.split(":", 1)[1]
    users[user_id]["gender"] = g
    users[user_id]["step"] = "ask_age"
    kb = InlineKeyboardMarkup()
    for a in age_options:
        kb.add(InlineKeyboardButton(a, callback_data=f"age:{a}"))
    await bot.send_message(user_id, "Ваш возраст:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("age:"))
async def process_age(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    a = callback_query.data.split(":", 1)[1]
    users[user_id]["age"] = a
    users[user_id]["step"] = "ask_work"
    kb = InlineKeyboardMarkup()
    for w in work_options:
        kb.add(InlineKeyboardButton(w, callback_data=f"work:{w}"))
    await bot.send_message(user_id, "Выберите вашу сферу деятельности:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("work:"))
async def process_work(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    w = callback_query.data.split(":", 1)[1]
    users[user_id]["work"] = w
    users[user_id]["step"] = "ask_what"
    await bot.send_message(user_id, "Что вас *зацепило* в названии курса?")

@dp.callback_query_handler(lambda c: c.data == "check_subscription")
async def process_subscription(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    if await check_subscription(user_id):
        await bot.send_message(user_id, "✨ Отлично, подписка подтверждена! Можно идти дальше 🚀")
        users[user_id]["step"] = "done"
    else:
        await bot.send_message(user_id, "Пока не вижу подписки 🤔 Проверь ещё раз и нажми «Я подписался».")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
