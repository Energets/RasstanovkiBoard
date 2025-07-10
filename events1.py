import tkinter as tk
from tkinter import simpledialog, colorchooser, messagebox, Menu
from model import state, get_figure_at, create_connection, NUM_COLS, NUM_ROWS, CELL_WIDTH, CELL_HEIGHT, CANVAS_OFFSET_X
from canvas_draw import draw_all, is_near_line

def on_mouse_down(event):
    fig = get_figure_at(event.x, event.y)
    if fig:
        state["dragged_figure"] = fig

def on_mouse_move(event):
    fig = state["dragged_figure"]
    if fig:
        gx = (event.x - CANVAS_OFFSET_X) // CELL_WIDTH
        gy = event.y // CELL_HEIGHT
        gx = max(0, min(NUM_COLS - 1, gx))
        gy = max(0, min(NUM_ROWS - 1, gy))
        fig["x"] = gx
        fig["y"] = gy
        draw_all(event.widget)

    if state.get("coord_label"):
        gx = (event.x - CANVAS_OFFSET_X) // CELL_WIDTH
        gy = event.y // CELL_HEIGHT
        if 0 <= gx < NUM_COLS and 0 <= gy < NUM_ROWS:
            state["coord_label"].config(text=f"Клетка: {chr(65 + gx)}{gy + 1}")
        else:
            state["coord_label"].config(text="Клетка: -")

def on_mouse_up(event):
    state["dragged_figure"] = None

def on_canvas_click(event):
    canvas = event.widget
    fig = get_figure_at(event.x, event.y)

    if state["creating_connection"] is not None:
        if fig:
            idx1 = state["creating_connection"]
            idx2 = state["figures"].index(fig)
            conn = create_connection(idx1, idx2)
            state["connections"].append(conn)
            state["creating_connection"] = None
            state["highlighted"] = None
            bind_canvas_events(canvas)
            draw_all(canvas)
        return
    else:
        if fig:
            state["highlighted"] = fig
            draw_all(canvas)

def on_double_click(event):
    canvas = event.widget
    fig = get_figure_at(event.x, event.y)
    if fig:
        canvas.after(10, lambda: rename_figure(canvas))
        return

    # Проверка попадания по связи
    for i, conn in enumerate(state["connections"]):
        try:
            f1 = state["figures"][conn["from"]]
            f2 = state["figures"][conn["to"]]
        except IndexError:
            continue
        x1 = CANVAS_OFFSET_X + f1["x"] * CELL_WIDTH + CELL_WIDTH // 2
        y1 = f1["y"] * CELL_HEIGHT + CELL_HEIGHT // 2
        x2 = CANVAS_OFFSET_X + f2["x"] * CELL_WIDTH + CELL_WIDTH // 2
        y2 = f2["y"] * CELL_HEIGHT + CELL_HEIGHT // 2
        if is_near_line(event.x, event.y, x1, y1, x2, y2):
            label = simpledialog.askstring("Подпись связи", "Введите подпись:", initialvalue=conn.get("label", ""))
            if label is not None:
                conn["label"] = label
                draw_all(canvas)
            return

def on_right_click(event):
    canvas = event.widget
    fig = get_figure_at(event.x, event.y)
    if fig:
        state["context_figure"] = fig
        menu = Menu(canvas, tearoff=0)
        menu.add_command(label="✏ Изменить подпись", command=lambda: canvas.after(10, lambda: rename_figure(canvas)))
        menu.add_command(label="🎨 Сменить цвет", command=lambda: canvas.after(10, lambda: change_color(canvas)))
        if state["phrases"].get("фигуры"):
            menu.add_command(label="💬 Вставить фразу", command=lambda: canvas.after(10, lambda: insert_phrase(canvas)))
        menu.add_command(label="🧭 Повернуть", command=lambda: canvas.after(10, lambda: rotate_direction(canvas)))
        menu.add_separator()
        menu.add_command(label="❌ Удалить", command=lambda: canvas.after(10, lambda: delete_figure(canvas)))
        menu.tk_popup(event.x_root, event.y_root)
        return

    # Если не фигура — ищем связь
    for i, conn in enumerate(state["connections"]):
        try:
            f1 = state["figures"][conn["from"]]
            f2 = state["figures"][conn["to"]]
        except IndexError:
            continue
        x1 = CANVAS_OFFSET_X + f1["x"] * CELL_WIDTH + CELL_WIDTH // 2
        y1 = f1["y"] * CELL_HEIGHT + CELL_HEIGHT // 2
        x2 = CANVAS_OFFSET_X + f2["x"] * CELL_WIDTH + CELL_WIDTH // 2
        y2 = f2["y"] * CELL_HEIGHT + CELL_HEIGHT // 2
        if is_near_line(event.x, event.y, x1, y1, x2, y2):
            def delete_conn(index=i):
                del state["connections"][index]
                draw_all(canvas)
            menu = Menu(canvas, tearoff=0)
            menu.add_command(label="🗑 Удалить связь", command=delete_conn)
            menu.tk_popup(event.x_root, event.y_root)
            return

def rename_figure(canvas):
    fig = state["context_figure"]
    roleFig = simpledialog.askstring("Подпись", "Введите подпись:", initialvalue=fig.get("role", ""))
    if roleFig is not None:
        fig["role"] = roleFig
        draw_all(canvas)

def change_color(canvas):
    fig = state["context_figure"]
    c = colorchooser.askcolor()[1]
    if c:
        fig["color"] = c
        draw_all(canvas)

def insert_phrase(canvas):
    fig = state["context_figure"]
    phrases = state["phrases"].get("фигуры", [])
    if phrases:
        phrase = simpledialog.askstring("Фраза", "Выберите или вставьте:", initialvalue=phrases[0])
        if phrase:
            fig["label"] = phrase  # 👈 меняем подфигурный текст
            draw_all(canvas)


def delete_figure(canvas):
    fig = state["context_figure"]
    idx = state["figures"].index(fig)
    state["figures"].remove(fig)
    state["connections"] = [c for c in state["connections"] if c["from"] != idx and c["to"] != idx]
    for c in state["connections"]:
        if c["from"] > idx: c["from"] -= 1
        if c["to"] > idx: c["to"] -= 1
    state["context_figure"] = None
    draw_all(canvas)

def rotate_direction(canvas):
    fig = state["context_figure"]
    dirs = ["up", "right", "down", "left"]
    current = fig.get("direction", "up")
    idx = (dirs.index(current) + 1) % 4
    fig["direction"] = dirs[idx]
    draw_all(canvas)

def start_connection():
    messagebox.showinfo("Связь", "Кликни по первой фигуре")
    def select_first(event):
        fig = get_figure_at(event.x, event.y)
        if fig:
            state["creating_connection"] = state["figures"].index(fig)
            state["highlighted"] = fig
            draw_all(event.widget)
            messagebox.showinfo("Связь", "Теперь кликни по второй фигуре")
            event.widget.bind("<Button-1>", on_canvas_click)
    return select_first

def bind_canvas_events(canvas):
    canvas.bind("<Button-1>", on_canvas_click)
    canvas.bind("<ButtonPress-1>", on_mouse_down)
    canvas.bind("<B1-Motion>", on_mouse_move)
    canvas.bind("<ButtonRelease-1>", on_mouse_up)
    canvas.bind("<Button-3>", on_right_click)
    canvas.bind("<Double-Button-1>", on_double_click)
