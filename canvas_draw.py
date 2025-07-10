import tkinter as tk
import string
import textwrap
from model import state, CELL_WIDTH, NUM_ROWS, CANVAS_OFFSET_X, get_role_image, LABEL_WRAP
from tkinter import font as tkFont
from model import CELL_HEIGHT, NUM_COLS
from math import atan2, cos, sin

def draw_grid(canvas):
    for i in range(NUM_COLS):
        for j in range(NUM_ROWS):
            x0 = CANVAS_OFFSET_X + i * CELL_WIDTH
            y0 = j * CELL_HEIGHT
            x1 = x0 + CELL_WIDTH
            y1 = y0 + CELL_HEIGHT
            canvas.create_rectangle(x0, y0, x1, y1, outline="lightgray")

    for i in range(NUM_COLS):
        canvas.create_text(CANVAS_OFFSET_X + i * CELL_WIDTH + CELL_WIDTH // 2,
                           NUM_ROWS * CELL_HEIGHT + 10, text=string.ascii_uppercase[i])
    for j in range(NUM_ROWS):
        canvas.create_text(CANVAS_OFFSET_X - 10, j * CELL_HEIGHT + CELL_HEIGHT // 2,
                           text=str(j + 1), anchor="e")

def draw_all(canvas):
    canvas.delete("all")
    canvas.configure(bg=state["settings"].get("background_color", "#ffffff"))
    if state["settings"].get("grid", True):
        draw_grid(canvas)
    for conn in state["connections"]:
        draw_connection(canvas, conn)
    for fig in state["figures"]:
        draw_figure(canvas, fig)

def draw_figure(canvas, fig):
    # Центр клетки
    cx = CANVAS_OFFSET_X + fig["x"] * CELL_WIDTH + CELL_WIDTH // 2
    cy = fig["y"] * CELL_HEIGHT + CELL_HEIGHT // 2
    r = int(CELL_WIDTH * 0.3)

    # Подсветка (если выделена)
    if fig == state.get("highlighted"):
        canvas.create_oval(cx - r - 5, cy - r - 5, cx + r + 5, cy + r + 5, outline="orange", width=3)

    # Настройки шрифта
    font_settings = state["settings"].get("default_font", {})
    family = font_settings.get("family", "Arial")
    size = font_settings.get("size", 10)
    color = font_settings.get("color", "#000000")
    style = font_settings.get("style", "normal")

    weight = "bold" if "bold" in style else "normal"
    slant = "italic" if "italic" in style else "roman"
    tk_font = tkFont.Font(family=family, size=size, weight=weight, slant=slant)

    # Получение изображения
    img = get_role_image(fig["role"]) if state["settings"].get("use_images") else None

    # Рисуем фигуру
    link_color = state["settings"].get("default_connection", {}).get("color", "black")
    if img:
        canvas.create_image(cx, cy, image=img)
        draw_nose(canvas, fig.get("direction", "up"), cx, cy, r, color=link_color)
    else:
        canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill=fig.get("color", "#aaccee"))
        draw_nose(canvas, fig.get("direction", "up"), cx, cy, r, color=link_color)

    # 🎭 Роль под фигурой (если отличается от фразы)
    if fig.get("role") and fig.get("label") != fig.get("role"):
        canvas.create_text(cx, cy + r + 12, text=fig["role"], font=tk_font, fill=color)

    # 💬 Фраза справа от фигуры (в несколько строк)
    label = fig.get("label", "")
    lines = textwrap.wrap(label, width=LABEL_WRAP)
    for i, line in enumerate(lines):
        canvas.create_text(cx + r + 15, cy - 10 + i * 14, text=line, anchor="w", font=tk_font, fill=color)

def draw_nose(canvas, direction, cx, cy, r, color="black"):
    dx = CELL_WIDTH * 0.15
    dy = CELL_HEIGHT * 0.15

    pts = []
    if direction == "up":
        pts = [cx, cy - r - dy, cx - dx, cy - r, cx + dx, cy - r]
    elif direction == "down":
        pts = [cx, cy + r + dy, cx - dx, cy + r, cx + dx, cy + r]
    elif direction == "left":
        pts = [cx - r - dx, cy, cx - r, cy - dy, cx - r, cy + dy]
    elif direction == "right":
        pts = [cx + r + dx, cy, cx + r, cy - dy, cx + r, cy + dy]
    elif direction == "up-right":
        pts = [cx + 2*dx, cy - r - dy, cx + dx, cy - r, cx + dx, cy - r - dy]
    elif direction == "down-right":
        pts = [cx + 2*dx, cy + r + dy, cx + dx, cy + r, cx + dx, cy + r + dy]
    elif direction == "down-left":
        pts = [cx - 2*dx, cy + r + dy, cx - dx, cy + r, cx - dx, cy + r + dy]
    elif direction == "up-left":
        pts = [cx - 2*dx, cy - r - dy, cx - dx, cy - r, cx - dx, cy - r - dy]

    if pts:
        canvas.create_polygon(pts, fill=color)

def draw_connection(canvas, conn):
    try:
        f1 = state["figures"][conn["from"]]
        f2 = state["figures"][conn["to"]]
    except IndexError:
        return

    # Центры фигур
    x1 = CANVAS_OFFSET_X + f1["x"] * CELL_WIDTH + CELL_WIDTH // 2
    y1 = f1["y"] * CELL_HEIGHT + CELL_HEIGHT // 2
    x2 = CANVAS_OFFSET_X + f2["x"] * CELL_WIDTH + CELL_WIDTH // 2
    y2 = f2["y"] * CELL_HEIGHT + CELL_HEIGHT // 2

    # Угол между точками
    dx = x2 - x1
    dy = y2 - y1
    angle = atan2(dy, dx)

    # Смещаем начало и конец линии, чтобы не касались центра фигуры
    offset = 25
    x1b = x1 + offset * cos(angle)
    y1b = y1 + offset * sin(angle)
    x2b = x2 - offset * cos(angle)
    y2b = y2 - offset * sin(angle)

    canvas.create_line(
        x1b, y1b, x2b, y2b,
        arrow=tk.LAST if conn.get("style", "arrow") == "arrow" else tk.NONE,
        fill=conn.get("color", "#000000"),
        width=conn.get("width", 2)
    )

    # Подпись связи
    if conn.get("label"):
        canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, text=conn["label"])


def is_near_line(x, y, x1, y1, x2, y2, tolerance=10):
    dx, dy = x2 - x1, y2 - y1
    if dx == dy == 0:
        return abs(x - x1) < tolerance and abs(y - y1) < tolerance
    t = max(0, min(1, ((x - x1)*dx + (y - y1)*dy) / (dx*dx + dy*dy)))
    proj_x = x1 + t * dx
    proj_y = y1 + t * dy
    return ((x - proj_x)**2 + (y - proj_y)**2)**0.5 <= tolerance
