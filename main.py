from aiogram import Bot, Dispatcher, executor, types
import json
import os

API_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

CHANNEL_USERNAME = "@merkulyevy_live_evolution_space"

lessons = {
    1: {
        "text": "📽 Урок 1. Здоровье можно поменять на деньги\n\nПосмотри видео:\n\n🔗 [Rutube](https://rutube.ru/video/private/438c67c0e3510477ba92ef1c9cbda807/?p=m8ZK3IF63nq3U8aiuKBfyQ)\n🔗 [YouTube](https://youtube.com/shorts/_uTHQopErp4)\n\n---\n\n📝 Задание:\n\nВспомни, пожалуйста, какие преодолённые тобой трудности укрепили твоё здоровье и помогли обрести внутреннюю силу и спокойствие?\n\nНапиши всё, что откликается.",
        "task": ""
    },
    2: {
        "text": "📽 Урок 2. Деньги могут спасти от старости и смерти\n\nПосмотри видео:\n\n🔗 [Rutube](https://rutube.ru/video/private/a455fedbc14d98eeac76e09dec70aaa8/?p=O-rFwwAB4tvSNHOJK5gDgw)\n🔗 [YouTube](https://youtube.com/shorts/6KOFfzMXeBo)\n\n---\n\n📝 Задание:\n\nРасскажи о моментах в своей жизни, когда деньги принесли тебе настоящее счастье и радость.\n\nБыли ли эпизоды, когда обладание ими стало источником огорчений и переживаний?", 
        "task": ""
    },
    3: {
        "text": "📽 Урок 3. Легкие деньги легко даются\n\nПосмотри видео:\n\n🔗 [Rutube](https://rutube.ru/video/private/ad9e2b3c210d21cd23712045627dab40/?p=Ib29o4dCFybWBwITaw8EcA)\n🔗 [YouTube](https://youtube.com/shorts/nzpJTNZseH8?feature=share)\n\n---\n\n📝 Задание:\n\nПоделись историей о том, как ты распорядился(ась) случайно обретёнными средствами.\n\nКакой полезный вывод ты сделал(а) из этого опыта?",
        "task": ""
    },
    4: {
        "text": "📽 Урок 4. Деньги можно сохранить без риска потерять\n\nПосмотри видео:\n\n🔗 [Rutube](https://rutube.ru/video/private/17cda71a3427edf4f8210bff14862bcd/?p=mC_3osWPMwJgbZ1mICPjOQ)\n🔗 [YouTube](https://youtube.com/shorts/nzpJTNZseH8?feature=share)\n\n---\n\n📝 Задание:\n\nКакие действия, на твой взгляд, уберегут тебя от потери денег и помогут защитить средства при хранении?",
        "task": ""
    },
    5: {
        "text": "📽 Урок 5. Купи сейчас, заплатишь потом\n\nПосмотри видео:\n\n🔗 [Rutube](https://rutube.ru/video/private/c190ba709164a4e7fe3f0c6be9ffd5d9/?p=OSf95L2cKiR_FfNmC9xzrg)\n🔗 [YouTube](https://youtube.com/shorts/wkbbH1NzmdY)\n\n---\n\n📝 Задание:\n\nКакие ценности и возможности остаются доступными человеку, если у него временно отсутствуют деньги?",
        "task": ""
    }
}

DATA_FILE = "data.json"
ADMIN_ID = 123456789

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

@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    user_id = str(message.from_user.id)
    data = load_data()
    if user_id not in data:
        data[user_id] = {"step": "ask_name", "answers": {}, "current": 1}
        save_data(data)

    await message.answer("👋 Привет! Это бот для мини-курса *Глюки про деньги*.\n\nПеред стартом давай немного познакомимся.")
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

@dp.message_handler(commands=["answers"])
async def send_answers(message: types.Message):
    user_data = get_user_data(message.from_user.id)
    answers = user_data.get("answers", {})
    if not answers:
        await message.answer("У тебя пока нет сохранённых ответов ✍️")
        return

    text = "📒 Твои ответы по курсу:\n\n"
    for num in sorted(answers, key=lambda x: int(x)):
        lesson = lessons.get(int(num), {}).get("text", f"Урок {num}")
        question = lesson.split("\n")[0]
        answer = answers[num]
        text += f"{question}\nОтвет: {answer}\n\n"

    await message.answer(text)

@dp.message_handler()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    step = user_data.get("step", "ask_name")

    if step == "ask_name":
        update_user_data(user_id, {"name": message.text.strip(), "step": "ask_company"})
        await message.answer("Напиши, пожалуйста, где ты работаешь и кем (можно в одной строке)")

    elif step == "ask_company":
        update_user_data(user_id, {"workplace": message.text.strip(), "step": "ask_contact"})
        await message.answer("Оставь контакт: номер телефона или ник в Телеграме, чтобы мы могли с тобой связаться, если что")

    elif step == "ask_contact":
        update_user_data(user_id, {"contact": message.text.strip(), "step": "ask_email"})
        await message.answer("И последнее — твой email:")

    elif step == "ask_email":
        update_user_data(user_id, {"email": message.text.strip(), "step": "lesson"})
        if await check_subscription(user_id):
            await message.answer("Отлично, начинаем ✨")
            await send_lesson(user_id, 1)
        else:
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(
                types.InlineKeyboardButton("🔔 Подписаться на канал", url="https://t.me/merkulyevy_live_evolution_space")
            )
            await message.answer(
                "⚠️ Чтобы пройти курс, нужно быть подписанным на наш канал.\n\nПодпишись и вернись — мы тебя ждём!",
                reply_markup=keyboard
            )
            update_user_data(user_id, {"step": "waiting_subscription"})

    elif step == "waiting_subscription":
        if await check_subscription(user_id):
            update_user_data(user_id, {"step": "lesson"})
            await message.answer("Отлично, начинаем ✨")
            await send_lesson(user_id, 1)
        else:
            await message.answer("Пока не вижу подписки. Проверь ещё раз и нажми сюда, когда подпишешься. 😊")

    elif step == "lesson":
        current = user_data.get("current", 1)
        if current > len(lessons):
            await message.answer("Курс завершён. Напиши /reset, чтобы начать заново. Или /answers — чтобы посмотреть свои ответы.")
            return
        update_user_data(user_id, {
            "answers": {**user_data.get("answers", {}), str(current): message.text.strip()},
            "current": current + 1
        })
        await send_lesson(user_id, current + 1)

async def send_lesson(user_id, lesson_id):
    lesson = lessons.get(lesson_id)
    if lesson:
        await bot.send_message(user_id, lesson['text'], parse_mode="Markdown")
    else:
        await bot.send_message(user_id, "Поздравляю, ты завершил(а) курс! 🎉\n\nХочешь посмотреть свои ответы? Напиши /answers")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
