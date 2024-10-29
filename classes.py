class Task:
    def __init__(self, text, id, creator, executors=None, reviewers=None):
        self.text = text
        self.id = id
        self.creator = creator
        self.executors = executors if executors else []
        self.reviewers = reviewers if reviewers else []

class KanbanBoard:
    def __init__(self):
        self.columns = {
            "Идеи": [],
            "В разработке": [],
            "Тестирование": [],
            "Проверка": [],
            "Готово": []
        }
        self.task_counter = 0

    def add_task(self, text, creator):
        """Добавляет новую задачу с уникальным ID в колонку 'Идеи'."""
        self.task_counter += 1
        task = Task(text=text, id=self.task_counter, creator=creator)
        self.columns['Идеи'].append(task)
        return task.id

    def move_task(self, id, from_column, to_column):
        """Перемещает задачу с указанным ID из одной колонки в другую."""
        task = self.get_task_by_id(id)
        if task:
            self.columns[from_column].remove(task)
            self.columns[to_column].append(task)

    def get_task_by_id(self, id):
        """Возвращает задачу по ее уникальному ID."""
        for column in self.columns.values():
            for task in column:
                if task.id == id:
                    return task
        return None

    def display_board(self):
        """Возвращает текстовое представление всех задач на доске."""
        board_str = ""
        for column_name, tasks in self.columns.items():
            board_str += f"{column_name}:\n"
            for task in tasks:
                board_str += f"- {task.id}: {task.text} (Creator: {task.creator})\n"
            board_str += "\n"
        return board_str
