import telebot
from telebot import types

bot = telebot.TeleBot("7983748330:AAFh96j12oGQMdm7a_nV5u0PySr0U9uKYiY")

@bot.message_handler(commands=["start"])
def main(message):
    bot.send_message(message.chat.id, f"Привет {message.from_user.username}, здесь вы можете составить план еды на неделю. Используй /help когда ничего не поймешь")

@bot.message_handler(commands=["help"])
def main(message):
    bot.send_message(message.chat.id, f"{message.from_user.username}, используй /создать, чтобы создать план (удивительно!!!), используй /план, чтобы посмотреть готовый план")


# Хранилище блюд: user_id → {'день': {'приём': 'блюдо'}}
meals = {}

# Временное состояние: user_id → (день, приём), ждём текст
waiting_for_input = {}

@bot.message_handler(commands=["создать"])
def start(message):
    markup = types.InlineKeyboardMarkup()
    for day in ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]:
        markup.add(types.InlineKeyboardButton(day, callback_data=day.lower()))
    bot.send_message(message.chat.id, "Выбери день недели:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"])
def choose_meal(call):
    day = call.data
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Завтрак", callback_data=f"{day}_завтрак"))
    markup.add(types.InlineKeyboardButton("Обед", callback_data=f"{day}_обед"))
    markup.add(types.InlineKeyboardButton("Ужин", callback_data=f"{day}_ужин"))
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=f"Вы выбрали {day.capitalize()}. Теперь выберите приём пищи:",
                          reply_markup=markup)

@bot.callback_query_handler(func=lambda call: "_завтрак" in call.data or "_обед" in call.data or "_ужин" in call.data)
def ask_for_dish(call):
    day, meal = call.data.split("_")
    user_id = call.from_user.id
    waiting_for_input[user_id] = (day, meal)
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, f"Что будешь есть на {meal} в {day}? Напиши текстом 🍽️")

@bot.message_handler(func=lambda message: message.from_user.id in waiting_for_input)
def save_dish(message):
    user_id = message.from_user.id
    day, meal = waiting_for_input.pop(user_id)
    dish = message.text

    if user_id not in meals:
        meals[user_id] = {}
    if day not in meals[user_id]:
        meals[user_id][day] = {}
    
    meals[user_id][day][meal] = dish

    bot.send_message(message.chat.id, f"Записала: {dish} на {meal} в {day.capitalize()}! 📝")

# Добавим команду чтобы посмотреть свой список
@bot.message_handler(commands=["план"])
def show_plan(message):
    user_id = message.from_user.id
    plan = meals.get(user_id, {})
    if not plan:
        bot.send_message(message.chat.id, "Пока что ты ничего не записал 😢")
        return
    text = "Твой план питания:\n\n"
    for day in plan:
        text += f"📅 {day.capitalize()}:\n"
        for meal in plan[day]:
            text += f"  🍽️ {meal.capitalize()}: {plan[day][meal]}\n"
        text += "\n"
    bot.send_message(message.chat.id, text)

bot.polling(non_stop=True)
