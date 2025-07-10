import os
import tkinter as tk
from model import CLIENTS_FOLDER, IMG_FOLDER, CANVAS_WIDTH, CANVAS_HEIGHT, state
from config import load_settings, load_phrases
from storage import load_last_client
from canvas_draw import draw_all
from events import bind_canvas_events
from ui_controls import create_buttons

if __name__ == "__main__":
    os.makedirs(CLIENTS_FOLDER, exist_ok=True)
    os.makedirs(IMG_FOLDER, exist_ok=True)

    load_settings()
    load_phrases()

    root = tk.Tk()
    root.title("Расстановки (плоская версия)")

    canvas = tk.Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="white")
    canvas.grid(row=0, column=0, columnspan=6, padx=(0, 10), pady=(10, 0))

    client_name = state["settings"].get("last_client", "")
    state["current_client"] = client_name
    root.title(f"Расстановка — {client_name}")

    # 💡 Label для координат
    coord_label = tk.Label(root, text="Клетка: -")
    coord_label.grid(row=1, column=0, columnspan=6, sticky="w", padx=10)
    state["coord_label"] = coord_label

    bind_canvas_events(canvas)
    create_buttons(root, canvas)
    load_last_client()
    draw_all(canvas)

    root.mainloop()

