# utils.py

from PIL import Image, ImageDraw, ImageFont
from kanban_board import KanbanBoard

def create_board_image(board: KanbanBoard) -> str:
    """
    Создает изображение канбан-доски.
    """
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    x_offset = 10

    for column_name, tasks in board.columns.items():
        draw.text((x_offset, 10), column_name, fill='black')
        y_offset = 40

        for task in tasks:
            draw.text((x_offset, y_offset), f"{task.id}: {task.text}", fill='blue')
            y_offset += 30

        x_offset += 200

    image_path = 'boards/board_image.png'
    img.save(image_path)
    return image_path

