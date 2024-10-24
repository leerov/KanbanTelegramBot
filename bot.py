# bot.py

import telebot
from telebot import types
from config import BOT_TOKEN, BOARD_PATH
from kanban_board import KanbanBoard, Task
from utils import create_board_image
import json
import os

bot = telebot.TeleBot(BOT_TOKEN)
boards = {}
messages = {}

def load_board(chat_id):
    # Загружаем доску из файла
    if os.path.exists(f"{BOARD_PATH}/{chat_id}.json"):
        with open(f"{BOARD_PATH}/{chat_id}.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
            board = KanbanBoard()
            board.columns = {k: [Task(**task) for task in v] for k, v in data['columns'].items()}
            return board
    return KanbanBoard()

def save_board(chat_id, board):
    # Сохраняем доску в файл
    with open(f"{BOARD_PATH}/{chat_id}.json", 'w', encoding='utf-8') as f:
        json.dump({'columns': {k: [task.__dict__ for task in v] for k, v in board.columns.items()}}, f)

@bot.message_handler(commands=['start'])
def start_command(message):
    chat_id = message.chat.id
    boards[chat_id] = boards.get(chat_id, load_board(chat_id))
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("Добавить задачу", "Показать доску", "Переместить задачу")
    bot.send_message(message.chat.id, "Привет! Я - канбан-бот. Что вы хотите сделать?", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Показать доску")
def show_board_handler(message):
    chat_id = message.chat.id
    if chat_id in boards:
        if chat_id in messages:
            bot.delete_message(chat_id, messages[chat_id])

        board_image_path = create_board_image(boards[chat_id])
        with open(board_image_path, 'rb') as img:
            msg = bot.send_photo(chat_id, img)
            messages[chat_id] = msg.message_id
    else:
        bot.send_message(message.chat.id, "Доска для этого чата еще не создана. Отправьте команду /start.")

@bot.message_handler(func=lambda message: message.text == "Переместить задачу")
def move_task_command(message):
    chat_id = message.chat.id
    if chat_id in boards:
        columns = list(boards[chat_id].columns.keys())
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for col in columns:
            markup.add(col)
        markup.add("Отмена")
        bot.send_message(chat_id, "Выберите колонку, из которой хотите переместить задачу:", reply_markup=markup)
        bot.register_next_step_handler(message, select_task_from_column)
    else:
        bot.send_message(message.chat.id, "Доска для этого чата еще не создана.")

def select_task_from_column(message):
    chat_id = message.chat.id
    column_name = message.text

    if column_name == "Отмена":
        bot.send_message(chat_id, "Перемещение задачи отменено.")
        return

    if column_name in boards[chat_id].columns:
        tasks = boards[chat_id].columns[column_name]
        if tasks:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for task in tasks:
                markup.add(task.text)
            markup.add("Назад")
            bot.send_message(chat_id, "Выберите задачу для перемещения:", reply_markup=markup)
            bot.register_next_step_handler(message, lambda msg: select_new_column(msg, column_name))
        else:
            bot.send_message(chat_id, "В этой колонке нет задач. Пожалуйста, выберите другую колонку.")
            move_task_command(message)  # Возвращаемся к выбору колонки
    else:
        bot.send_message(chat_id, "Колонка не найдена. Пожалуйста, выберите снова.")
        move_task_command(message)

def select_new_column(message, old_column_name):
    chat_id = message.chat.id
    task_text = message.text

    if task_text == "Назад":
        move_task_command(message)
        return

    task = None
    for t in boards[chat_id].columns[old_column_name]:
        if t.text == task_text:
            task = t
            break

    if task:
        new_columns = list(boards[chat_id].columns.keys())
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for col in new_columns:
            markup.add(col)
        markup.add("Отмена")
        bot.send_message(chat_id, "Выберите колонку, в которую хотите переместить задачу:", reply_markup=markup)
        bot.register_next_step_handler(message, lambda msg: move_selected_task(msg, task, old_column_name))
    else:
        bot.send_message(chat_id, "Задача не найдена. Пожалуйста, попробуйте снова.")
        move_task_command(message)

def move_selected_task(message, task, old_column_name):
    chat_id = message.chat.id
    new_column_name = message.text

    if new_column_name == "Отмена":
        bot.send_message(chat_id, "Перемещение задачи отменено.")
        return

    if new_column_name in boards[chat_id].columns:
        boards[chat_id].move_task(task.id, old_column_name, new_column_name)
        save_board(chat_id, boards[chat_id])
        bot.send_message(chat_id, f"Задача '{task.text}' перемещена из '{old_column_name}' в '{new_column_name}'.")
    else:
        bot.send_message(chat_id, "Ошибка: Неверная колонка.")

@bot.message_handler(commands=['add_task'])
def add_task_command(message):
    # Логика добавления задачи (например, с помощью текстового сообщения)
    pass

# Остальные обработчики остаются без изменений

if __name__ == "__main__":
    bot.polling(none_stop=True)

