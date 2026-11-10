
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import *
from logic import *
import sqlite3
import time
from datetime import date

bot = telebot.TeleBot(TOKEN)

QUESTIONS = {
    1: 'Как оформить заказ?',
    2: 'Как узнать статус моего заказа?',
    3: 'Как отменить заказ?',
    4: 'Что делать, если товар пришел поврежденным?',
    5: 'Как связаться с вашей технической поддержкой?',
    6: 'Как узнать информацию о доставке?'
}


def build_markup(message, prefix):
    bot.send_chat_action(message.chat.id, 'typing')
    time.sleep(2)

    markup = InlineKeyboardMarkup()

    btn1 = InlineKeyboardButton(
        'Как оформить заказ?', callback_data=f'{prefix}_1'
    )
    btn2 = InlineKeyboardButton(
        'Как узнать статус моего заказа?', callback_data=f'{prefix}_2'
    )
    btn3 = InlineKeyboardButton(
        'Как отменить заказ?', callback_data=f'{prefix}_3'
    )
    btn4 = InlineKeyboardButton(
        'Что делать, если товар пришел поврежденным?',
        callback_data=f'{prefix}_4'
    )
    btn5 = InlineKeyboardButton(
        'Как связаться с вашей технической поддержкой?',
        callback_data=f'{prefix}_5'
    )
    btn6 = InlineKeyboardButton(
        'Как узнать информацию о доставке?',
        callback_data=f'{prefix}_6'
    )

    markup.row(btn1)
    markup.row(btn2)
    markup.row(btn3)
    markup.row(btn4)
    markup.row(btn5)
    markup.row(btn6)

    bot.send_message(
        message.chat.id,
        'Выберите вашу проблему или вопрос:',
        reply_markup=markup
    )


def get_answer_from_db(question_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT answer FROM answers WHERE question_id = ?", (question_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else "Ответ не найден"


def save_user_answer_to_db(question_id, user_id, answer, question):
    conn = sqlite3.connect(DATABASE)
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(answer_id) FROM answers WHERE question_id = ?", (question_id,))
        row = cursor.fetchone()
        answer_id = (row[0] or 0) + 1
        cursor.execute(
            '''INSERT INTO answers (question_id, question, answer_id, user_id, answer)
               VALUES (?, ?, ?, ?, ?)''',
            (question_id, question, answer_id, user_id, answer)
        )
    conn.close()


def save_problem_to_db(user_id, problem):
    conn = sqlite3.connect(DATABASE)
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(problem_id) FROM problems")
        row = cursor.fetchone()
        problem_id = (row[0] or 0) + 1
        cursor.execute(
            '''INSERT INTO problems (problem_id, user_id, problem, date)
               VALUES (?, ?, ?, ?)''',
            (problem_id, user_id, problem, int(date.today().strftime('%Y%m%d')))
        )
    conn.close()


@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Привет! Я Бот, Который Поможет Тебе С Тех. Проблемами И С Покупками!")
    bot.send_message(message.chat.id, "Напиши мне /help и узнаешь подробности.")


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, "Введи /questions, и тебе будут предложены часто задаваемые вопросы. Нажми на любой и ты получишь ответ.")
    bot.send_message(message.chat.id, "Напиши мне /answers, и ты можешь сам ответить на эти вопросы")
    bot.send_message(message.chat.id, "Напиши мне /problem, чтобы сообщить о проблеме")


@bot.message_handler(commands=['questions'])
def choose_question(message):
    build_markup(message, 'view')


@bot.callback_query_handler(func=lambda call: call.data.startswith('view_'))
def show_answer(call):
    question_id = int(call.data.split('_')[1])
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, get_answer_from_db(question_id))
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)


@bot.message_handler(commands=['answers'])
def give_answer(message):
    build_markup(message, 'answer')


@bot.callback_query_handler(func=lambda call: call.data.startswith('answer_'))
def ask_user_answer(call):
    question_id = int(call.data.split('_')[1])
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, f"Напишите ваш ответ на вопрос:\n«{QUESTIONS[question_id]}»")
    bot.register_next_step_handler(call.message, save_user_answer, question_id, call.from_user.id, QUESTIONS[question_id])


def save_user_answer(message, question_id, user_id, question):
    if message.text and message.text.startswith('/'):
        bot.send_message(message.chat.id, "Ответ не сохранён. Введите /answers, чтобы попробовать снова.")
        return
    save_user_answer_to_db(question_id, user_id, message.text, question)
    bot.send_message(message.chat.id, "Ваш ответ сохранён. Спасибо!")


@bot.message_handler(commands=['problem'])
def report_problem(message):
    bot.send_message(message.chat.id, "Опишите вашу проблему одним сообщением.")
    bot.register_next_step_handler(message, save_user_problem, message.from_user.id)


def save_user_problem(message, user_id):
    if message.text and message.text.startswith('/'):
        bot.send_message(message.chat.id, "Проблема не сохранена. Введите /problem, чтобы попробовать снова.")
        return
    save_problem_to_db(user_id, message.text)
    bot.send_message(message.chat.id, "Ваша проблема сохранена. Мы свяжемся с вами!")


if __name__ == '__main__':
    manager = DB_Manager(DATABASE)
    manager.create_database()
    manager.create_table()
