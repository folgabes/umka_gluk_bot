from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import json
import os

API_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=API_TOKEN, parse_mode="Markdown")
dp = Dispatcher(bot)

CHANNEL_USERNAME = "@merkulyevy_live_evolution_space"
DATA_FILE = "data.json"
ADMIN_ID = 123456789  # замени на свой Telegram ID

# ---------------- УРОКИ ----------------
lessons = {
    1: {
        "question": "Вспомни, пожалуйста, какие преодолённые тобой трудности укрепили твоё здоровье и помогли обрести внутреннюю силу и спокойствие?",
        "text": "📽 Урок 1. Здоровье можно поменять на деньги\n\nПосмотри видео:\n\n🔗 [Rutube](https://rutube.ru/video/private/438c67c0e3510477ba92ef1c9cbda807/?p=m8ZK3IF63nq3U8aiuKBfyQ)\n🔗 [YouTube](https://youtube.com/shorts/_uTHQopErp4)\n\n---\n\n📝 Задание:\n\nВспомни, пожалуйста, какие преодолённые тобой трудности укрепили твоё здоровье и помогли обрести внутреннюю силу и спокойствие?",
    },
    2: {
        "question": "Расскажи о моментах в своей жизни, когда деньги принесли тебе настоящее счастье и радость. Были ли эпизоды, когда обладание ими стало источником огорчений и переживаний?",
        "text": "📽 Урок 2. Деньги могут спасти от старости и смерти\n\nПосмотри видео:\n\n🔗 [Rutube](https://rutube.ru/video/private/a455fedbc14d98eeac76e09dec70aaa8/?p=O-rFwwAB4tvSNHOJK5gDgw)\n🔗 [YouTube](https://youtube.com/shorts/6KOFfzMXeBo)\n\n---\n\n📝 Задание:\n\nРасскажи о моментах в своей жизни, когда деньги принесли тебе настоящее счастье и радость.\n\nБыли ли эпизоды, когда обладание ими стало источником огорчений и переживаний?",
    },
    3: {
        "question": "Поделись историей о том, как ты распорядился(ась) случайно обретёнными средствами. Какой полезный вывод ты сделал(а) из этого опыта?",
        "text": "📽 Урок 3. Легкие деньги легко даются\n\nПосмотри видео:\n\n🔗 [Rutube](https://rutube.ru/video/private/ad9e2b3c210d21cd23712045627dab40/?p=Ib29o4dCFybWBwITaw8EcA)\n🔗 [YouTube](https://youtube.com/shorts/nzpJTNZseH8?feature=share)\n\n---\n\n📝 Задание:\n\nПоделись историей о том, как ты распорядился(ась) случайно обретёнными средствами.\n\nКакой полезный вывод ты сделал(а) из этого опыта?",
    },
    4: {
        "question": "Какие действия, на твой взгляд, уберегут тебя от потери денег и помогут защитить средства при хранении?",
        "text": "📽 Урок 4. Деньги можно сохранить без риска потерять\n\nПосмотри видео:\n\n🔗 [Rutube](https://rutube.ru/video/private/17cda71a3427edf4f8210bff14862bcd/?p=mC_3osWPMwJgbZ1mICPjOQ)\n🔗 [YouTube](https://youtube.com/shorts/nzpJTNZseH8?feature=share)\n\n---\n\n📝 Задание:\n\nКакие действия, на твой взгляд, уберегут тебя от потери денег и помогут защитить средства при хранении?",
    },
    5: {
        "question": "Какие ценности и возможности остаются доступными человеку, если у него временно отсутствуют деньги?",
        "text": "📽 Урок 5. Купи сейчас, заплатишь потом\n\nПосмотри видео:\n\n🔗 [Rutube](https://rutube.ru/video/private/c190ba709164a4e7fe3f0c6be9ffd5d9/?p=OSf95L2cKiR_FfNmC9xzrg)\n🔗 [YouTube](https://youtube.com/shorts/wkbbH1NzmdY)\n\n---\n\n📝 Задание:\n\nКакие ценности и возможности остаются доступными человеку, если у него временно отсутствуют деньги?",
    },
}

# ---------------- ДАННЫЕ ----------------
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

async def check_subscription(user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ---------------- КОМАНДЫ ----------------
@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    update_user_data(message.from_user.id, {"step": "ask_name"})
    await message.answer("👋 Привет! Это бот для мини-курса *Глюки про деньги*.\n\nКак тебя зовут?")

@dp.message_handler(commands=["reset"])
async def reset_cmd(message: types.Message):
    data = load_data()
    user_id = str(message.from_user.id)
    if user_id in data:
        del data[user_id]
        save_data(data)
    await message.answer("Прогресс обнулён. Напиши /start, чтобы начать заново.")

@dp.message_handler(commands=["help"])
async def help_cmd(message: types.Message):
    await bot.send_message(ADMIN_ID, f"🆘 Помощь от @{message.from_user.username} ({message.from_user.id})")
    await message.answer("Запрос отправлен куратору. Мы скоро свяжемся с тобой.")

@dp.message_handler(commands=["answers"])
async def answers_cmd(message: types.Message):
    user_data = get_user_data(message.from_user.id)
    answers = user_data.get("answers", {})
    if not answers:
        await message.answer("У тебя пока нет сохранённых ответов ✍️")
        return

    text = "📒 Твои ответы по курсу:\n\n"
    for num in sorted(answers, key=lambda x: int(x)):
        question = lessons[int(num)]["question"]
        answer = answers[num]
        text += f"📽 Урок {num}. {question}\nОтвет: {answer}\n\n"

    await message.answer(text)

# ---------------- АНКЕТА ----------------
@dp.message_handler()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    step = user_data.get("step", "ask_name")

    if step == "ask_name":
        update_user_data(user_id, {"name": message.text.strip(), "step": "ask_work"})
        await message.answer("Напиши, пожалуйста, где ты работаешь и кем.")

    elif step == "ask_work":
        update_user_data(user_id, {"work": message.text.strip(), "step": "ask_contact"})
        await message.answer("Оставь контакт: телефон или ник в Telegram.")

    elif step == "ask_contact":
        update_user_data(user_id, {"contact": message.text.strip(), "step": "ask_email"})
        await message.answer("И последнее — твой email:")

    elif step == "ask_email":
        update_user_data(user_id, {"email": message.text.strip(), "step": "waiting_subscription"})
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("🔔 Подписаться на канал", url="https://t.me/merkulyevy_live_evolution_space"))
        keyboard.add(InlineKeyboardButton("✅ Я подписался", callback_data="check_subscription"))
        await message.answer(
            "⚠️ Чтобы пройти курс, нужно быть подписанным на наш канал.\n\nПодпишись и нажми «Я подписался».",
            reply_markup=keyboard
        )

    elif step == "lesson":
        current = user_data.get("current", 1)
        if current > len(lessons):
            await message.answer("Курс завершён 🎉\n\nНапиши /answers, чтобы посмотреть свои ответы.")
            return
        # сохраняем ответ
        answers = user_data.get("answers", {})
        answers[str(current)] = message.text.strip()
        update_user_data(user_id, {"answers": answers, "current": current + 1})
        await send_lesson(user_id, current + 1)

# ---------------- CALLBACK ----------------
@dp.callback_query_handler(lambda c: c.data == "check_subscription")
async def process_subscription(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    if await check_subscription(user_id):
        update_user_data(user_id, {"step": "lesson", "current": 1})
        await bot.send_message(user_id, "Отлично, подписка подтверждена ✨ Начинаем курс!")
        await send_lesson(user_id, 1)
    else:
        await bot.send_message(user_id, "Пока не вижу подписки 🤔 Проверь ещё раз и нажми «Я подписался».")

# ---------------- УРОКИ ----------------
async def send_lesson(user_id, lesson_id):
    lesson = lessons.get(lesson_id)
    if lesson:
        await bot.send_message(user_id, lesson["text"])
    else:
        await bot.send_message(user_id, "Поздравляю, ты завершил(а) курс! 🎉\n\nНапиши /answers, чтобы посмотреть свои ответы.")

# ---------------- ЗАПУСК ----------------
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
