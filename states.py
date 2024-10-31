MOVE_MODE = "moving_task"
DEFAULT_MODE = "default"
ADD_MODE = = "add_task"

def enter_move_mode(chat_id):
        user_states[chat_id] = MOVE_MODE

def exit_move_mode(chat_id):
    if chat_id in user_states:
        del user_states[chat_id]

def is_in_move_mode(chat_id):
    return user_states.get(chat_id) == MOVE_MODE

def enter_default_mode(chat_id):
    user_states[chat_id] = DEFAULT_MODE

def is_in_default_mode(chat_id):
    return user_states.get(chat_id) == DEFAULT_MODE

def enter_add_mode(chat_id):
    user_states[chat_id] = ADD_MODE

def exit_add_mode(chat_id):
    if chat_id in user_states:
        del user_states[chat_id]
