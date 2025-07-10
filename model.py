import os
import json
import tkinter as tk
from tkinter import simpledialog
from PIL import Image, ImageTk

CELL_WIDTH = 80
CELL_HEIGHT = 80
NUM_COLS = 8
NUM_ROWS = 6
CANVAS_OFFSET_X = 40  # отступ слева для отображения цифр
CANVAS_EXTRA_Y = 40   # отступ снизу под кнопки

CANVAS_WIDTH = CANVAS_OFFSET_X + CELL_WIDTH * NUM_COLS
CANVAS_HEIGHT = CELL_HEIGHT * NUM_ROWS + CANVAS_EXTRA_Y

IMG_FOLDER = "IMG"
CLIENTS_FOLDER = "clients"
LABEL_WRAP = 20  # количество символов до переноса

state = {
    "figures": [],
    "connections": [],
    "dragged_figure": None,
    "role_counters": {},
    "image_cache": {},
    "highlighted": None,
    "creating_connection": None,
    "current_client": None,
    "settings": {},
    "phrases": {},
    "coord_label": None,  # 💡 для отображения координат
    "background_color": "#ffffff",  # или любой другой по умолчанию
}

def create_figure(role, x, y, label="", color="#aaccee"):
    return {"role": role, "x": x, "y": y, "label": label, "color": color}

def create_connection(from_idx, to_idx):
    s = state["settings"].get("default_connection", {})
    return {
        "from": from_idx,
        "to": to_idx,
        "label": "",
        "style": s.get("style", "arrow"),
        "color": s.get("color", "#000000"),
        "width": s.get("width", 2)
    }

def get_figure_at(x, y):
    r = CELL_WIDTH * 0.4  # Радиус захвата
    for fig in reversed(state["figures"]):  # Сначала проверяем верхние
        cx = CANVAS_OFFSET_X + fig["x"] * CELL_WIDTH + CELL_WIDTH // 2
        cy = fig["y"] * CELL_HEIGHT + CELL_HEIGHT // 2
        if ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5 <= r:
            return fig
    return None

def get_auto_role(base_role):
    count = state["role_counters"].get(base_role, 1)
    state["role_counters"][base_role] = count + 1
    return f"{base_role} {count}"

def get_role_image(role):
    name = state["settings"].get("image_map", {}).get(role, f"{role}.png")
    path = os.path.join(IMG_FOLDER, name)
    if not os.path.exists(path):
        return None

    if role not in state["image_cache"]:
        try:
            img = tk.PhotoImage(file=path)

            # 👇 масштабируем под CELL_WIDTH
            iw, ih = img.width(), img.height()
            factor_w = max(1, iw // CELL_WIDTH)
            factor_h = max(1, ih // CELL_HEIGHT)
            scale = max(factor_w, factor_h)+1
            if scale > 1:
                img = img.subsample(scale)

            state["image_cache"][role] = img
        except Exception as e:
            print(f"Ошибка загрузки картинки для роли '{role}': {e}")
            return None

    return state["image_cache"][role]



