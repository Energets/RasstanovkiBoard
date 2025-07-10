import os
import json
import tkinter as tk
from tkinter import simpledialog, colorchooser, messagebox, filedialog
import tkinter.font as tkFont
from model import state, CLIENTS_FOLDER
from events import start_connection
from config import save_settings
from canvas_draw import draw_all
from storage import save_to_json, load_from_json, save_to_excel, save_as_image, load_last_client

def create_buttons(root, canvas):
    button_frame = tk.Frame(root)
    button_frame.grid(row=1, column=0, columnspan=6, pady=(10, 0))
    buttons = [
        ("➕ Добавить", lambda: add_figure(canvas)),
        ("🔗 Связь", lambda: canvas.bind("<Button-1>", start_connection())),
        ("📊 Excel", lambda: save_to_excel()),
        ("💾 Сохранить", save_to_json),
        ("📂 Загрузить", lambda: (load_from_json(), draw_all(canvas))),
        ("🖼 PNG", lambda: save_as_image(canvas)),
        ("⚙ Настройки", lambda: open_settings_dialog(canvas))
    ]
    for text, cmd in buttons:
        tk.Button(button_frame, text=text, command=cmd).pack(side="left", padx=4)

def add_figure(canvas):
    role = simpledialog.askstring("Роль", "Введите базовое имя роли:")
    if not role:
        return
    name = get_auto_name(role)
    fig = {
        "role": name,
        "x": 2,
        "y": 2,
        "label": "",
        "color": "#aaccee",
        "direction": "up"
    }
    state["figures"].append(fig)
    draw_all(canvas)

def get_auto_name(base):
    count = sum(1 for f in state["figures"] if f["role"].startswith(base))
    return f"{base} {count + 1}"

def open_settings_dialog1(canvas):
    win = tk.Toplevel()
    win.title("Настройки")
    win.grab_set()

    font = state["settings"].get("default_font", {})
    conn = state["settings"].get("default_connection", {})
    entries = {}

    fonts_available = sorted(tkFont.families())
    font_family_var = tk.StringVar(value=font.get("family", "Arial"))
    style_var = tk.StringVar(value=font.get("style", "normal"))

    # === Шрифт ===
    tk.Label(win, text="Шрифт:").grid(row=0, column=0, sticky="e")
    tk.OptionMenu(win, font_family_var, *fonts_available).grid(row=0, column=1, sticky="w")

    tk.Label(win, text="Размер:").grid(row=1, column=0, sticky="e")
    entries["font_size"] = tk.Entry(win)
    entries["font_size"].insert(0, str(font.get("size", 10)))
    entries["font_size"].grid(row=1, column=1)

    tk.Label(win, text="Стиль:").grid(row=2, column=0, sticky="e")
    tk.OptionMenu(win, style_var, "normal", "bold", "italic", "bold italic").grid(row=2, column=1, sticky="w")

    tk.Label(win, text="Цвет текста:").grid(row=3, column=0, sticky="e")
    def choose_font_color():
        c = colorchooser.askcolor()[1]
        if c:
            entries["font_color"].delete(0, tk.END)
            entries["font_color"].insert(0, c)
    entries["font_color"] = tk.Entry(win)
    entries["font_color"].insert(0, font.get("color", "#000000"))
    entries["font_color"].grid(row=3, column=1)
    tk.Button(win, text="...", command=choose_font_color).grid(row=3, column=2)

    # === Связи ===
    tk.Label(win, text="Цвет связи:").grid(row=4, column=0, sticky="e")
    def choose_line_color():
        c = colorchooser.askcolor()[1]
        if c:
            entries["line_color"].delete(0, tk.END)
            entries["line_color"].insert(0, c)
    entries["line_color"] = tk.Entry(win)
    entries["line_color"].insert(0, conn.get("color", "#000000"))
    entries["line_color"].grid(row=4, column=1)
    tk.Button(win, text="...", command=choose_line_color).grid(row=4, column=2)

    tk.Label(win, text="Толщина связи:").grid(row=5, column=0, sticky="e")
    entries["line_width"] = tk.Entry(win)
    entries["line_width"].insert(0, str(conn.get("width", 2)))
    entries["line_width"].grid(row=5, column=1)

    tk.Label(win, text="Стиль связи:").grid(row=6, column=0, sticky="e")
    style_conn_var = tk.StringVar(value=conn.get("style", "arrow"))
    tk.OptionMenu(win, style_conn_var, "arrow", "line").grid(row=6, column=1, sticky="w")

    # === Чекбоксы ===
    grid_var = tk.BooleanVar(value=state["settings"].get("grid", True))
    label_var = tk.BooleanVar(value=state["settings"].get("show_labels", True))
    image_var = tk.BooleanVar(value=state["settings"].get("use_images", True))

    tk.Checkbutton(win, text="Показывать сетку", variable=grid_var).grid(row=7, column=0, columnspan=2, sticky="w")
    tk.Checkbutton(win, text="Показывать подписи", variable=label_var).grid(row=8, column=0, columnspan=2, sticky="w")
    tk.Checkbutton(win, text="Использовать изображения", variable=image_var).grid(row=9, column=0, columnspan=2, sticky="w")

    # === Цвет фона ===
    tk.Label(win, text="Цвет фона:").grid(row=10, column=0, sticky="e")
    def choose_bg_color():
        c = colorchooser.askcolor()[1]
        if c:
            entries["background_color"].delete(0, tk.END)
            entries["background_color"].insert(0, c)
    entries["background_color"] = tk.Entry(win)
    entries["background_color"].insert(0, state["settings"].get("background_color", "#ffffff"))
    entries["background_color"].grid(row=10, column=1)
    tk.Button(win, text="...", command=choose_bg_color).grid(row=10, column=2)

    # === Шаблоны ===
    def apply_template(name):
        presets = {
            "Пастельный": {
                "background_color": "#f6f3ef",
                "default_font": {"family": "Verdana", "size": 12, "color": "#555555", "style": "normal"},
                "default_connection": {"color": "#888888", "width": 2, "style": "line"}
            },
            "Ночной": {
                "background_color": "#1e1e1e",
                "default_font": {"family": "Consolas", "size": 12, "color": "#cccccc", "style": "bold"},
                "default_connection": {"color": "#00ccff", "width": 2, "style": "arrow"}
            },
            "Контрастный": {
                "background_color": "#ffffff",
                "default_font": {"family": "Arial", "size": 12, "color": "#000000", "style": "bold italic"},
                "default_connection": {"color": "#ff0000", "width": 3, "style": "arrow"}
            }
        }
        if name in presets:
            state["settings"].update(presets[name])
            save_settings()
            draw_all(canvas)
            win.destroy()

    row = 13
    column = 0
    for name in ["Пастельный", "Ночной", "Контрастный"]:
##        tk.Button(win, text=f"Шаблон: {name}", command=lambda n=name: apply_template(n)).grid(row=row, column=0, pady=4)
##        row += 1
        tk.Button(win, text=f"Шаблон: {name}", command=lambda n=name: apply_template(n)).grid(row=row, column=column, padx=4, pady=4)
        column += 1

        # === Применить ===
    def apply_and_close():
        try:
            font["family"] = font_family_var.get()
            font["size"] = int(entries["font_size"].get())
            font["color"] = entries["font_color"].get()
            font["style"] = style_var.get()
            conn["color"] = entries["line_color"].get()
            conn["width"] = int(entries["line_width"].get())
            conn["style"] = style_conn_var.get()
            state["settings"]["grid"] = grid_var.get()
            state["settings"]["show_labels"] = label_var.get()
            state["settings"]["use_images"] = image_var.get()
            state["settings"]["background_color"] = entries["background_color"].get()
            save_settings()
            draw_all(canvas)
            win.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    row += 1
    tk.Button(win, text="Роли и изображения", command=lambda: open_role_image_map(canvas)).grid(row=row, column=0, columnspan=2, pady=4)

    tk.Button(win, text="Применить", command=apply_and_close).grid(row=row+1, column=1, pady=10)
    tk.Button(win, text="Закрыть", command=win.destroy).grid(row=row+1, column=2, pady=10)

def open_settings_dialog(canvas):
    import tkinter.font as tkFont

    win = tk.Toplevel()
    win.title("Настройки")
    win.grab_set()

    font = state["settings"].get("default_font", {})
    conn = state["settings"].get("default_connection", {})
    entries = {}

    fonts_available = sorted(tkFont.families())
    font_family_var = tk.StringVar(value=font.get("family", "Arial"))
    style_var = tk.StringVar(value=font.get("style", "normal"))

    # === Шрифт ===
    tk.Label(win, text="Шрифт:").grid(row=0, column=0, sticky="e")
    tk.OptionMenu(win, font_family_var, *fonts_available).grid(row=0, column=1, sticky="w")

    tk.Label(win, text="Размер:").grid(row=1, column=0, sticky="e")
    entries["font_size"] = tk.Entry(win)
    entries["font_size"].insert(0, str(font.get("size", 10)))
    entries["font_size"].grid(row=1, column=1)

    tk.Label(win, text="Стиль:").grid(row=2, column=0, sticky="e")
    tk.OptionMenu(win, style_var, "normal", "bold", "italic", "bold italic").grid(row=2, column=1, sticky="w")

    tk.Label(win, text="Цвет текста:").grid(row=3, column=0, sticky="e")
    def choose_font_color():
        c = colorchooser.askcolor()[1]
        if c:
            entries["font_color"].delete(0, tk.END)
            entries["font_color"].insert(0, c)
    entries["font_color"] = tk.Entry(win)
    entries["font_color"].insert(0, font.get("color", "#000000"))
    entries["font_color"].grid(row=3, column=1)
    tk.Button(win, text="...", command=choose_font_color).grid(row=3, column=2)

    # === Связи ===
    tk.Label(win, text="Цвет связи:").grid(row=4, column=0, sticky="e")
    def choose_line_color():
        c = colorchooser.askcolor()[1]
        if c:
            entries["line_color"].delete(0, tk.END)
            entries["line_color"].insert(0, c)
    entries["line_color"] = tk.Entry(win)
    entries["line_color"].insert(0, conn.get("color", "#000000"))
    entries["line_color"].grid(row=4, column=1)
    tk.Button(win, text="...", command=choose_line_color).grid(row=4, column=2)

    tk.Label(win, text="Толщина связи:").grid(row=5, column=0, sticky="e")
    entries["line_width"] = tk.Entry(win)
    entries["line_width"].insert(0, str(conn.get("width", 2)))
    entries["line_width"].grid(row=5, column=1)

    tk.Label(win, text="Стиль связи:").grid(row=6, column=0, sticky="e")
    style_conn_var = tk.StringVar(value=conn.get("style", "arrow"))
    tk.OptionMenu(win, style_conn_var, "arrow", "line").grid(row=6, column=1, sticky="w")

    # === Чекбоксы ===
    grid_var = tk.BooleanVar(value=state["settings"].get("grid", True))
    label_var = tk.BooleanVar(value=state["settings"].get("show_labels", True))
    image_var = tk.BooleanVar(value=state["settings"].get("use_images", True))

    tk.Checkbutton(win, text="Показывать сетку", variable=grid_var).grid(row=7, column=0, columnspan=2, sticky="w")
    tk.Checkbutton(win, text="Показывать подписи", variable=label_var).grid(row=8, column=0, columnspan=2, sticky="w")
    tk.Checkbutton(win, text="Использовать изображения", variable=image_var).grid(row=9, column=0, columnspan=2, sticky="w")

    # === Цвет фона ===
    tk.Label(win, text="Цвет фона:").grid(row=10, column=0, sticky="e")
    def choose_bg_color():
        c = colorchooser.askcolor()[1]
        if c:
            entries["background_color"].delete(0, tk.END)
            entries["background_color"].insert(0, c)
    entries["background_color"] = tk.Entry(win)
    entries["background_color"].insert(0, state["settings"].get("background_color", "#ffffff"))
    entries["background_color"].grid(row=10, column=1)
    tk.Button(win, text="...", command=choose_bg_color).grid(row=10, column=2)

    row = 11

    # === Кнопка соответствия ролей и картинок ===
    tk.Button(win, text="Роли и изображения", command=lambda: open_role_image_map(canvas)).grid(row=row, column=0, columnspan=3, pady=6)
    row += 1

    # === Шаблоны ===
    def apply_template(name):
        presets = {
            "Пастельный": {
                "background_color": "#f6f3ef",
                "default_font": {"family": "Verdana", "size": 12, "color": "#555555", "style": "normal"},
                "default_connection": {"color": "#888888", "width": 2, "style": "line"}
            },
            "Ночной": {
                "background_color": "#1e1e1e",
                "default_font": {"family": "Consolas", "size": 12, "color": "#cccccc", "style": "bold"},
                "default_connection": {"color": "#00ccff", "width": 2, "style": "arrow"}
            },
            "Контрастный": {
                "background_color": "#ffffff",
                "default_font": {"family": "Arial", "size": 12, "color": "#000000", "style": "bold italic"},
                "default_connection": {"color": "#ff0000", "width": 3, "style": "arrow"}
            }
        }
        if name in presets:
            state["settings"].update(presets[name])
            save_settings()
            draw_all(canvas)
            win.destroy()

##    for name in ["Пастельный", "Ночной", "Контрастный"]:
##        tk.Button(win, text=f"Шаблон: {name}", command=lambda n=name: apply_template(n)).grid(row=row, column=0, columnspan=3, pady=4)
##        row += 1
        # === Шаблоны в одну строку ===
    preset_frame = tk.Frame(win)
    preset_frame.grid(row=row, column=0, columnspan=3, pady=6)

    for name in ["Пастельный", "Ночной", "Контрастный"]:
        tk.Button(preset_frame, text=name, command=lambda n=name: apply_template(n)).pack(side="left", padx=4)
    row += 1


    # === Применение и закрытие ===
    def apply_and_close():
        try:
            font["family"] = font_family_var.get()
            font["size"] = int(entries["font_size"].get())
            font["color"] = entries["font_color"].get()
            font["style"] = style_var.get()
            conn["color"] = entries["line_color"].get()
            conn["width"] = int(entries["line_width"].get())
            conn["style"] = style_conn_var.get()
            state["settings"]["grid"] = grid_var.get()
            state["settings"]["show_labels"] = label_var.get()
            state["settings"]["use_images"] = image_var.get()
            state["settings"]["background_color"] = entries["background_color"].get()
            save_settings()
            draw_all(canvas)
            win.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    tk.Button(win, text="Применить", command=apply_and_close).grid(row=row, column=1, padx=10, pady=12)
    tk.Button(win, text="Закрыть", command=win.destroy).grid(row=row, column=2, padx=10, pady=12)

def open_role_image_map(canvas):
    from tkinter import filedialog
    import os

    w = tk.Toplevel()
    w.title("Роли и изображения")
    w.geometry("500x400")
    w.grab_set()

    roles = sorted(set(f["role"] for f in state["figures"]))
    rows = []

    for i, role in enumerate(roles):
        tk.Label(w, text=role).grid(row=i, column=0, sticky="e", padx=5, pady=2)
        entry = tk.Entry(w, width=30)
        current = state["settings"].get("image_map", {}).get(role, f"{role}.png")
        entry.insert(0, current)
        entry.grid(row=i, column=1, padx=5, pady=2)

        def choose_file(e=entry):
            path = filedialog.askopenfilename(filetypes=[("PNG изображения", "*.png")])
            if path:
                e.delete(0, tk.END)
                e.insert(0, os.path.basename(path))

        tk.Button(w, text="...", command=choose_file).grid(row=i, column=2)
        rows.append((role, entry))

    def apply():
        image_map = {}
        for role, entry in rows:
            filename = entry.get().strip()
            if filename:
                image_map[role] = filename
                state["image_cache"].pop(role, None)
        state["settings"]["image_map"] = image_map
        save_settings()
        draw_all(canvas)
        w.destroy()

    tk.Button(w, text="Применить изображения", command=apply).grid(row=len(roles)+2, column=1, pady=10)
