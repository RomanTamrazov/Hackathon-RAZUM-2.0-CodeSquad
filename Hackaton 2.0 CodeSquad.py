import telebot
import random
TOKEN = "8065173763:AAGh3SQyqxTslMB80V8o0TZH257K-0_H7BU"
bot = telebot.TeleBot(TOKEN)
tasks = {}
MOTIVATIONAL_QUOTES = [
    "Успех — это сумма небольших усилий, повторяющихся каждый день!",
    "Каждая ошибка — это еще один шаг к успеху!",
    "Никогда не сдавайся, потому что именно тот момент, когда ты готов сдаться, часто оказывается точкой перелома!",
    "Только те, кто рискуют идти слишком далеко, могут узнать, как далеко они могут зайти!",
    "Делай сегодня то, что другие не хотят, завтра будешь жить так, как другие не могут!"
]
#-----------------------------
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    tasks[user_id] = tasks.get(user_id, [])
    bot.send_message(user_id, "Привет! Я твой школьный планировщик.📅\nДля помощи с командами напиши - /help")

@bot.message_handler(commands=['motivate'])
def motivate(message):
    bot.send_message(message.chat.id, f"💪 {random.choice(MOTIVATIONAL_QUOTES)}")
#-------------------------------
@bot.message_handler(commands=['add'])
def add_task(message):
    user_id = message.chat.id
    try:
        _, category, task_text, time_str = message.text.split("/", maxsplit=3)
        tasks[user_id].append({"category": category.strip(), "text": task_text.strip(), "time": time_str.strip(), "done": False})
        bot.send_message(user_id, f"✅ Добавлена задача в категорию {category.strip()} - {task_text.strip()} в {time_str.strip()}")
    except:
        bot.send_message(user_id, "⚠️ Ошибка! Используй формат: /add Категория / Задача / ЧАС:МИН")
#-------------------------------
@bot.message_handler(commands=['list'])
def list_tasks(message):
    user_id = message.chat.id
    if user_id in tasks and tasks[user_id]:
        task_list = "\n".join([f"{i+1}. [{t['category']}] {t['text']} в {t['time']} {'✅' if t['done'] else '⏳'}" for i, t in enumerate(tasks[user_id])])
        bot.send_message(user_id, f"📋 Твои задачи:\n{task_list}")
    else:
        bot.send_message(user_id, "📭 У тебя пока что нет задач.")
#---------------------------
@bot.message_handler(commands=['done'])
def mark_done(message):
    user_id = message.chat.id
    try:
        task_num = int(message.text.split()[1]) - 1
        if 0 <= task_num < len(tasks.get(user_id, [])):
            tasks[user_id][task_num]["done"] = True
            bot.send_message(user_id, f"✅ Задача '{tasks[user_id][task_num]['text']}' выполнена!")
        else:
            bot.send_message(user_id, "⚠️ Неверный номер задачи.")
    except:
        bot.send_message(user_id, "⚠️ Используй: /done [номер задачи]")
#--------------------------
@bot.message_handler(commands=['delete'])
def delete_task(message):
    user_id = message.chat.id
    try:
        task_num = int(message.text.split()[1]) - 1
        if 0 <= task_num < len(tasks.get(user_id, [])):
            task_text = tasks[user_id].pop(task_num)["text"]
            bot.send_message(user_id, f"🗑 Задача '{task_text}' удалена.")
        else:
            bot.send_message(user_id, "⚠️ Неверный номер задачи.")
    except:
        bot.send_message(user_id, "⚠️ Используй: /delete [номер задачи]")
#---------------------------
@bot.message_handler(commands=['calendar'])
def show_calendar(message):
    """Показывает задачи в формате календаря"""
    user_id = message.chat.id
    if user_id not in tasks or not tasks[user_id]:
        bot.send_message(user_id, "📭 У тебя нет задач.")
        return
    
    tasks_sorted = sorted(tasks[user_id], key=lambda t: t["time"])
    calendar_view = "\n".join([
        f"{t['time']} - [{t['category']}] {t['text']} {'✅' if t['done'] else '⏳'}"
        for t in tasks_sorted
    ])
    
    bot.send_message(user_id, f"📅 *Твой календарь задач:*\n{calendar_view}", parse_mode="Markdown")
#---------------------------
@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.chat.id, """
📌 *Команды:*
/add Категория / Задача / ЧАС:МИН - добавить задачу
/list - показать задачи
/done [номер] - отметить выполненной ✅
/delete [номер] - удалить задачу ❌
/calendar - показать календарь 📅
/motivate - мотивацию надо поднять
/help - помощь
""", parse_mode="Markdown")
print("Бот запущен! Можете пробовать :)")
bot.polling(none_stop=True)