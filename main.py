from aiogram import Bot, Dispatcher, executor, types
import os
import json
import asyncio

API_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = "@merkulyevy_live_evolution_space"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

DATA_FILE = "data.json"

# ---- Уроки ----
lessons = {
    1: {
        "question": "Вспомни, пожалуйста, какие преодолённые тобой трудности укрепили твоё здоровье и помогли обрести внутреннюю силу и спокойствие?",
        "text": "📽 Урок 1. Здоровье можно поменять на деньги\n\n🔗 [Rutube](https://rutube.ru/video/private/438c67c0e3510477ba92ef1c9cbda807/?p=m8ZK3IF63nq3U8aiuKBfyQ)\n🔗 [YouTube](https://youtube.com/shorts/_uTHQopErp4)\n\n---\n\n📝 Задание:\n\nВспомни, пожалуйста, какие преодолённые тобой трудности укрепили твоё здоровье и помогли обрести внутреннюю силу и спокойствие?"
    },
    2: {
        "question": "Расскажи о моментах в своей жизни, когда деньги принесли тебе настоящее счастье и радость. Были ли эпизоды, когда обладание ими стало источником огорчений и переживаний?",
        "text": "📽 Урок 2. Деньги могут спасти от старости и смерти\n\n🔗 [Rutube](https://rutube.ru/video/private/a455fedbc14d98eeac76e09dec70aaa8/?p=O-rFwwAB4tvSNHOJK5gDgw)\n🔗 [YouTube](https://youtube.com/shorts/6KOFfzMXeBo)\n\n---\n\n📝 Задание:\n\nРасскажи о моментах в своей жизни, когда деньги принесли тебе настоящее счастье и радость. Были ли эпизоды, когда обладание ими стало источником огорчений и переживаний?"
    },
    3: {
        "question": "Поделись историей о том, как ты распорядился(ась) случайно обретёнными средствами. Какой полезный вывод ты сделал(а) из этого опыта?",
        "text": "📽 Урок 3. Легкие деньги легко даются\n\n🔗 [Rutube](https://rutube.ru/video/private/ad9e2b3c210d21cd23712045627dab40/?p=Ib29o4dCFybWBwITaw8EcA)\n🔗 [YouTube](https://youtube.com/shorts/nzpJTNZseH8)\n\n---\n\n📝 Задание:\n\nПоделись историей о том, как ты распорядился(ась) случайно обретёнными средствами. Какой полезный вывод ты сделал(а) из этого опыта?"
    },
    4: {
        "question": "Какие действия, на твой взгляд, уберегут тебя от потери денег и помогут защитить средства при хранении?",
        "text": "📽 Урок 4. Деньги можно сохранить без риска потерять\n\n🔗 [Rutube](https://rutube.ru/video/private/17cda71a3427edf4f8210bff14862bcd/?p=mC_3osWPMwJgbZ1mICPjOQ)\n🔗 [YouTube](https://youtube.com/shorts/nzpJTNZseH8)\n\n---\n\n📝 Задание:\n\nКакие действия, на твой взгляд, уберегут тебя от потери денег и помогут защитить средства при хранении?"
    },
    5: {
        "question": "Какие ценности и возможности остаются доступными человеку, если у него временно отсутствуют деньги?",
        "text": "📽 Урок 5. Купи сейчас, заплатишь потом\n\n🔗 [Rutube](https://rutube.ru/video/private/c190ba709164a4e7fe3f0c6be9ffd5d9/?p=OSf95L2cKiR_FfNmC9xzrg)\n🔗 [YouTube](https://youtube.com/shorts/wkbbH1NzmdY)\n\n---\n\n📝 Задание:\n\nКакие ценности и возможности остаются доступными человеку, если у него временно отсутствуют деньги?"
    },
}

# ---- Хранилище ----
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_user(user_id):
    data = load_data()
    return data.get(str(user_id), {"step": "start", "answers": {}, "current": 1})

def update_user(user_id, new_data):
    data = load_data()
    uid = str(user_id)
    if uid not in data:
        data[uid] = {"step": "start", "answers": {}, "current": 1}
    data[uid].update(new_data)
    save_data(data)

# ---- Проверка подписки ----
async def check_subscription(user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ---- Команды ----
@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    user = get_user(user_id)

    if user["step"] == "start":
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        keyboard.add("Начать")
        await message.answer("Привет! 👋 Я бот для курса. Нажми кнопку, чтобы начать.", reply_markup=keyboard)

@dp.message_handler(lambda m: m.text == "Начать")
async def start_registration(message: types.Message):
    update_user(message.from_user.id, {"step": "ask_name"})
    await message.answer("Как тебя зовут?", reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler(commands=["answers"])
async def answers_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    answers = user.get("answers", {})
    if not answers:
        await message.answer("Ответов пока нет ✍️")
        return
    text = "📒 Твои ответы по курсу:\n\n"
    for num, ans in answers.items():
        q = lessons[int(num)]["question"]
        text += f"📽 Урок {num}. {q}\nОтвет: {ans}\n\n"
    await message.answer(text)

# ---- Логика диалога ----
@dp.message_handler()
async def main_flow(message: types.Message):
    user_id = message.from_user.id
    user = get_user(user_id)
    step = user["step"]

    if step == "ask_name":
        update_user(user_id, {"name": message.text, "step": "ask_email"})
        await message.answer("Оставь, пожалуйста, свой email:")

    elif step == "ask_email":
        update_user(user_id, {"email": message.text, "step": "ask_gender"})
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add("Мужчина", "Женщина")
        await message.answer("Укажи свой пол:", reply_markup=kb)

    elif step == "ask_gender":
        update_user(user_id, {"gender": message.text, "step": "ask_age"})
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add("до 20", "20-30", "31-45", "46-60", "больше 60")
        await message.answer("Укажи свой возраст:", reply_markup=kb)

    elif step == "ask_age":
        update_user(user_id, {"age": message.text, "step": "ask_field"})
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add("предприниматель", "свой бизнес", "фрилансер")
        kb.add("руководитель в найме", "сотрудник в найме", "не работаю")
        await message.answer("Выбери сферу деятельности:", reply_markup=kb)

    elif step == "ask_field":
        update_user(user_id, {"field": message.text, "step": "check_sub"})
        await message.answer("Спасибо! Теперь нужно подписаться на канал 👉 https://t.me/merkulyevy_live_evolution_space\n\nКогда подпишешься — напиши 'Готово'.")

    elif step == "check_sub":
        if message.text.lower() == "готово":
            if await check_subscription(user_id):
                update_user(user_id, {"step": "lesson"})
                await message.answer(lessons[1]["text"], reply_markup=types.ReplyKeyboardRemove())
            else:
                await message.answer("❗️ Я не вижу подписки. Подпишись и напиши 'Готово'.")
        else:
            await message.answer("Напиши 'Готово', когда подпишешься.")

    elif step == "lesson":
        current = user["current"]
        update_user(user_id, {"answers": {**user["answers"], str(current): message.text}})
        next_lesson = current + 1
        if next_lesson in lessons:
            update_user(user_id, {"current": next_lesson})
            await message.answer(lessons[next_lesson]["text"])
        else:
            update_user(user_id, {"step": "done"})
            await message.answer("🎉 Ты прошёл все уроки! Спасибо за участие.")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(dp.start_polling(bot))
    loop.run_forever()
