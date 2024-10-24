# kanban_board.py

import json

class Task:
    def __init__(self, text, task_id, creator, executors=None, reviewers=None):
        self.text = text
        self.id = task_id
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

    def add_task(self, text, creator):
        task_id = len(self.columns['To Do']) + len(self.columns['In Progress']) + len(self.columns['Done']) + 1
        task = Task(text, task_id, creator)
        self.columns['To Do'].append(task)
        return task_id

    def move_task(self, task_id, from_column, to_column):
        task = self.get_task_by_id(task_id)
        if task:
            self.columns[from_column].remove(task)
            self.columns[to_column].append(task)

    def get_task_by_id(self, task_id):
        for column in self.columns.values():
            for task in column:
                if task.id == task_id:
                    return task
        return None

    def display_board(self):
        board_str = ""
        for column_name, tasks in self.columns.items():
            board_str += f"{column_name}:\n"
            for task in tasks:
                board_str += f"- {task.id}: {task.text} (Creator: {task.creator})\n"
            board_str += "\n"
        return board_str

