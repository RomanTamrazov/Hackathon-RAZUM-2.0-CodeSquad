import telebot
import random
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import time
import datetime
import threading
import pytz
TOKEN = "8065173763:AAGh3SQyqxTslMB80V8o0TZH257K-0_H7BU"
bot = telebot.TeleBot(TOKEN)
tasks = {}
MOTIVATIONAL_QUOTES = [
    "Успех — это сумма небольших усилий, повторяющихся каждый день!",
    "Каждая ошибка — это еще один шаг к успеху!",
    "Никогда не сдавайся, потому что именно тот момент, когда ты готов сдаться, часто оказывается точкой перелома!",
    "Только те, кто рискуют идти слишком далеко, могут узнать, как далеко они могут зайти!",
    "Делай сегодня то, что другие не хотят, завтра будешь жить так, как другие не могут!",
    "Трудности – это трамплин к успеху. Прыгай выше!",
    "Каждый день – это шанс стать лучше, чем вчера.",
    "Сегодня ты работаешь на свою мечту, а завтра мечта работает на тебя!",
    "Не бойся неудач – бойся бездействия!",
    "Большие достижения начинаются с маленьких шагов. Главное – не останавливаться!",
    "Если у тебя есть мечта – у тебя уже есть силы её достичь!",
    "Настоящая магия начинается, когда ты выходишь из зоны комфорта.",
    "Делай шаг за шагом, и однажды ты окажешься там, где мечтал быть.",
    "Не сравнивай себя с другими – сравнивай себя с собой вчерашним.",
    "Успех любит настойчивых – продолжай двигаться вперёд!"
]
moscow_tz = pytz.timezone("Europe/Moscow")
#------------------------
def get_moscow_time():
    return datetime.datetime.now(moscow_tz).strftime("%H:%M")
now = get_moscow_time()
#------------------------
def main_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("/add"), KeyboardButton("/list"), KeyboardButton("/categories"))
    keyboard.add(KeyboardButton("/done"), KeyboardButton("/delete"), KeyboardButton("/important"))
    keyboard.add(KeyboardButton("/motivate"), KeyboardButton("/help"))
    return keyboard
#------------------------
def check_reminders():
    while True:
        current_time = get_moscow_time()
        for user_id in tasks:
            for task in tasks[user_id]:
                if not task["done"] and task["time"] == current_time:
                    bot.send_message(user_id, f"⏰ Напоминание! {task['categoty']} {task['text']}")
        time.sleep(60)
threading.Thread(target=check_reminders, daemon=True).start()
#------------------------------
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    tasks[user_id] = tasks.get(user_id, [])
    bot.send_message(user_id, "Привет! Я твой школьный планировщик.📅\nДля помощи с командами напиши - /help", reply_markup=main_menu())
#-------------------------------
@bot.message_handler(commands=['motivate'])
def motivate(message):
    bot.send_message(message.chat.id, f"💪 {random.choice(MOTIVATIONAL_QUOTES)}")
#-------------------------------
@bot.message_handler(commands=['add'])
def add_task(message):
    user_id = message.chat.id
    try:
        parts = message.text.split("/", maxsplit=3)
        if len(parts) < 4:
            raise ValueError("Недостаточно аргументов")
        category, task_text, time_str = parts[1][3:].strip(), parts[2].strip(), parts[3].strip()
        tasks[user_id].append({"category": category, "text": task_text, "time": time_str, "done": False, "important": False})
        bot.send_message(user_id, f"✅ Добавлена задача в категорию {category} - {task_text} в {time_str}")
    except:
        bot.send_message(user_id, "⚠️ Ошибка! Используй: Категория/Задача/Час:Минуты ")
#-------------------------------
@bot.message_handler(commands=['categories'])
def show_categories(message):
    user_id = message.chat.id
    if user_id not in tasks or not tasks[user_id]:
        bot.send_message(user_id, "📭 У тебя пока что нет задач.")
        return
    categories = set(task["category"] for task in tasks[user_id])
    bot.send_message(user_id, "📂 *Твои категории:*\n" + "\n".join(f"🔹 {c}" for c in categories), parse_mode="Markdown")
#-------------------------------
@bot.message_handler(commands=['list'])
def list_tasks(message):
    user_id = message.chat.id
    args = message.text.split(maxsplit=1)
    category_filter = args[1].strip().lower() if len(args) > 1 else None
    if user_id not in tasks or not tasks[user_id]:
        bot.send_message(user_id, "📭 У тебя пока что нет задач.")
        return
    filtered_tasks = tasks[user_id]
    if category_filter:
        filtered_tasks = [t for t in filtered_tasks if t["category"].lower() == category_filter]
    if not filtered_tasks:
        bot.send_message(user_id, "🔍 В этой категории пока нет задач.")
        return
    filtered_tasks.sort(key=lambda x: not x["important"])
    task_list = "\n".join([
        f"{i+1}. {'🔥' if t['important'] else ''} [{t['category']}] {t['text']} в {t['time']} {'✅' if t['done'] else '⏳'}"
        for i, t in enumerate(filtered_tasks)
    ])
    bot.send_message(user_id, f"📋 *Твои задачи:*\n{task_list}", parse_mode="Markdown")
#-----------------------------
@bot.message_handler(commands=['important'])
def mark_important(message):
    user_id = message.chat.id
    try:
        task_num = int(message.text.split()[1]) - 1
        if 0 <= task_num < len(tasks.get(user_id, [])):
            tasks[user_id][task_num]["important"] = True
            bot.send_message(user_id, f"🔥 Задача '{tasks[user_id][task_num]['text']}' теперь важная!")
        else:
            bot.send_message(user_id, "⚠️ Неверный номер задачи.")
    except:
        bot.send_message(user_id, "⚠️ Используй: /important [номер задачи]")
#-----------------------------
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
#------------------------------
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
#-------------------------------
@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.chat.id, """
📌 *Команды:*
/add Категория / Задача / ЧАС:МИНУТЫ - добавить задачу
/list - показать задачи
/list [категория] - показать задачи в категориях
/categories - показать все категории
/done [номер] - отметить выполненной ✅
/delete [номер] - удалить задачу ❌
/important [номер] - отметить задачу как важную 🔥
/motivate - мотивацию надо поднять
/help - помощь
""", parse_mode="Markdown", reply_markup=main_menu())
print("Бот запущен! Можете пробовать :)")
bot.polling(none_stop=True)
