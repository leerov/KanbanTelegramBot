import os

# Словарь с переменными и значениями по умолчанию
config_variables = {
    'BOT_TOKEN': 'None',
    'BOARD_PATH': '"boards/"'
}

# Имя файла конфигурации
config_file = 'config.py'

# Проверяем, существует ли файл config.py
if not os.path.exists(config_file):
    with open(config_file, 'w') as f:
        f.write("# config.pynn")

# Перебираем переменные и запрашиваем значения
for key, default_value in config_variables.items():
    user_input = input(f"Введите значение для {key} (по умолчанию: {default_value}): ")
    
    # Если пользователь не ввел ничего, используем значение по умолчанию
    if user_input.strip() == "":
        user_input = default_value

    # Записываем переменную в файл config.py
    with open(config_file, 'a') as f:
        f.write(f"{key} = {user_input}\n")

print(f"Файл {config_file} успешно создан и заполнен.")
