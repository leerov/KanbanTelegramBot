import os, io
from PIL import Image, ImageDraw, ImageFont
from kanban_board import KanbanBoard

BACKGROUND_COLOR = (34, 34, 34)
COLUMN_NAME_COLOR = (200, 200, 200)
TASK_TEXT_COLOR = (255, 255, 255)
CARD_BACKGROUND_COLOR = (47, 79, 79)
CARD_BORDER_COLOR = (100, 149, 237)
COLUMN_DIVIDER_COLOR = (255, 255, 255)

def create_board_image(board: KanbanBoard) -> str:
    font_path = 'fonts/DejaVuSans.ttf'
    font = ImageFont.truetype(font_path, 16)

    # Определения констант
    column_padding = 20
    card_padding = 10
    header_height = 40
    cards_per_row = 2
    card_width = 200
    card_height = 60
    column_width = card_width * cards_per_row + (cards_per_row - 1) * card_padding
    max_tasks_in_column = max(len(tasks) for tasks in board.columns.values())
    num_rows = (max_tasks_in_column + cards_per_row - 1) // cards_per_row
    column_height = header_height + num_rows * (card_height + card_padding) - card_padding
    image_width = len(board.columns) * (column_width + column_padding) - column_padding + 20
    image_height = column_height + 20

    # Создание изображения
    img = Image.new('RGB', (image_width, image_height), color=BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)
    x_offset = 10

    for column_name, tasks in board.columns.items():
        text_bbox = draw.textbbox((0, 0), column_name, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        draw.text((x_offset + (column_width - text_width) / 2, 10), column_name, fill=COLUMN_NAME_COLOR, font=font)
        y_offset = header_height

        for i, task in enumerate(tasks):
            row = i // cards_per_row
            col = i % cards_per_row
            card_x = x_offset + col * (card_width + card_padding)
            card_y = y_offset + row * (card_height + card_padding)
            draw.rectangle(
                [card_x, card_y, card_x + card_width, card_y + card_height],
                fill=CARD_BACKGROUND_COLOR,
                outline=CARD_BORDER_COLOR,
                width=2
            )
            task_text = f"{task.id}: {task.text}"
            text_bbox = draw.textbbox((0, 0), task_text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            text_x = card_x + (card_width - text_width) / 2
            text_y = card_y + (card_height - text_height) / 2
            draw.text((text_x, text_y), task_text, fill=TASK_TEXT_COLOR, font=font)

        # Рисование разделителей
        divider_y_start = 10
        divider_y_end = image_height - 10
        divider_x = x_offset + column_width + column_padding // 2
        draw.line([(divider_x, divider_y_start), (divider_x, divider_y_end)], fill=COLUMN_DIVIDER_COLOR, width=2)

        x_offset += column_width + column_padding

    # Сразу возвращаем изображение без сохранения
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    return img_byte_arr  # Возвращаем поток изображения

if __name__ == "__main__":
    board = KanbanBoard()
    for i in range(200):
        board.add_task(f"Задача {i + 1}", "Админ")
    create_board_image(board)
