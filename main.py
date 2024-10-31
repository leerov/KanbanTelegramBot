import telebot
from telebot import types
from config import BOT_TOKEN, BOARD_PATH
from classes import KanbanBoard, Task
from boardImage import create_board_image
import states
import json
import os

bot = telebot.TeleBot(BOT_TOKEN)
boards = {}
messages = {}
user_states = {}

def load_board(chat_id):
    """Загружает доску пользователя из JSON-файла или создает новую, если файла нет."""
    board_path = f"{BOARD_PATH}/{chat_id}.json"
    if not os.path.exists(board_path):
        return KanbanBoard()

    with open(board_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    board = KanbanBoard()
    board.columns = {
        column_name: [
            Task(
                id=task.get('id', board.task_counter + 1),  # Генерация id, если его нет
                text=task['text'],
                creator=task.get('creator')
            )
            for task in tasks
        ]
        for column_name, tasks in data['columns'].items()
    }
    return board

def save_board(chat_id, board):
    """Сохраняет текущую доску пользователя в JSON-файл."""
    board_path = f"{BOARD_PATH}/{chat_id}.json"
    board_data = {
        'columns': {
            column_name: [task.__dict__ for task in tasks]
            for column_name, tasks in board.columns.items()
        }
    }
    with open(board_path, 'w', encoding='utf-8') as file:
        json.dump(board_data, file)

@bot.message_handler(commands=['start'])
def start_command(message):
    chat_id = message.chat.id
    boards[chat_id] = load_board(chat_id)
    states.enter_default_mode(chat_id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("Добавить задачу", "Показать доску", "Переместить задачу")
    bot.send_message(chat_id, "Что вы хотите сделать?", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Показать доску")
def show_board_handler(message):
    chat_id = message.chat.id
    if chat_id in boards:
        if chat_id in messages:
            bot.delete_message(chat_id, messages[chat_id])

        board_image = create_board_image(boards[chat_id])
        messages[chat_id] = bot.send_photo(chat_id, board_image)
        bot.pin_chat_message(chat_id, messages[chat_id])

@bot.message_handler(func=lambda message: message.text == "Переместить задачу")
def move_task_command(message):
    chat_id = message.chat.id
    if chat_id in boards:
        states.enter_move_mode(chat_id)
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
        states.exit_move_mode(chat_id)
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
            bot.send_message(chat_id, "В этой колонке нет задач.")
            move_task_command(message)
    else:
        bot.send_message(chat_id, "Колонка не найдена.")
        move_task_command(message)

def select_new_column(message, old_column_name):
    chat_id = message.chat.id
    task_text = message.text

    if task_text == "Назад":
        move_task_command(message)
        return

    task = next((t for t in boards[chat_id].columns[old_column_name] if t.text == task_text), None)
    if task:
        new_columns = list(boards[chat_id].columns.keys())
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for col in new_columns:
            markup.add(col)
        markup.add("Отмена")
        bot.send_message(chat_id, "Выберите колонку, в которую хотите переместить задачу:", reply_markup=markup)
        bot.register_next_step_handler(message, lambda msg: move_selected_task(msg, task, old_column_name))
    else:
        bot.send_message(chat_id, "Задача не найдена.")
        move_task_command(message)

def move_selected_task(message, task, old_column_name):
    chat_id = message.chat.id
    new_column_name = message.text

    if new_column_name == "Отмена":
        states.exit_move_mode(chat_id)
        bot.send_message(chat_id, "Перемещение задачи отменено.")
        return

    if new_column_name in boards[chat_id].columns:
        boards[chat_id].move_task(task.id, old_column_name, new_column_name)
        save_board(chat_id, boards[chat_id])
        bot.send_message(chat_id, f"Задача '{task.text}' перемещена.")
        start_command(message=message)
    else:
        bot.send_message(chat_id, "Ошибка: Неверная колонка.")

@bot.message_handler(func=lambda message: message.text == "Добавить задачу")
def add_task_command(message):
    chat_id = message.chat.id
    if chat_id in boards:
        states.enter_add_mode(chat_id)
        bot.send_message(chat_id, "Введите текст новой задачи:")
        bot.register_next_step_handler(message, lambda msg: add_task(msg, chat_id))
    else:
        bot.send_message(chat_id, "Доска для этого чата еще не создана. Отправьте команду /start.")

def add_task(message, chat_id):
    text = message.text
    boards[chat_id].add_task(text, message.from_user.id)
    save_board(chat_id, boards[chat_id])
    states.exit_add_mode(chat_id)
    bot.send_message(chat_id, f"Задача '{text}' добавлена.")

