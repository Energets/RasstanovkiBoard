##модуль 5 из 6 — storage.py 💾 Этот модуль управляет сохранением и загрузкой всего контекста:
##.json для клиентов
##.xlsx для Excel
##.png в виде изображения
##загрузку последнего клиента

import os
import json
from tkinter import simpledialog, messagebox, filedialog
from model import state, CLIENTS_FOLDER
from config import save_settings
import openpyxl
from PIL import Image

def save_to_json():
    name = simpledialog.askstring("Клиент", "Имя клиента:")
    if not name:
        return
    state["current_client"] = name
    os.makedirs(CLIENTS_FOLDER, exist_ok=True)
    with open(os.path.join(CLIENTS_FOLDER, f"{name}.json"), "w", encoding="utf-8") as f:
        json.dump({"figures": state["figures"], "connections": state["connections"]}, f, indent=2, ensure_ascii=False)
    state["settings"]["last_client"] = name
    save_settings()
    messagebox.showinfo("Сохранено", f"Состояние клиента '{name}' сохранено.")

def load_from_json():
    import os
    import json
    from tkinter import filedialog, messagebox
    from model import state, CLIENTS_FOLDER

    path = filedialog.askopenfilename(
        title="Выберите файл клиента",
        initialdir=CLIENTS_FOLDER,
        filetypes=[("JSON-файлы", "*.json")]
    )

    if not path:
        return

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        state["figures"] = data.get("figures", [])
        state["connections"] = data.get("connections", [])
        state["current_client"] = os.path.splitext(os.path.basename(path))[0]
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось загрузить клиента:\n{e}")

def save_to_excel():
    if not state["current_client"]:
        messagebox.showwarning("Клиент", "Сначала задай имя клиента.")
        return
    filename = filedialog.asksaveasfilename(defaultextension=".xlsx",
        filetypes=[("Excel файлы", "*.xlsx")],
        initialfile=f"{state['current_client']}.xlsx")
    if not filename:
        return
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = state["current_client"]
    ws.append(["Role", "X", "Y", "Label", "Color"])
    for fig in state["figures"]:
        ws.append([fig["role"], fig["x"], fig["y"], fig.get("label", ""), fig["color"]])
    ws2 = wb.create_sheet("Connections")
    ws2.append(["From", "To", "Label", "Style", "Color", "Width"])
    for conn in state["connections"]:
        ws2.append([
            conn["from"], conn["to"], conn.get("label", ""),
            conn.get("style", "arrow"), conn.get("color", "#000000"), conn.get("width", 2)
        ])
    wb.save(filename)
    messagebox.showinfo("Excel", f"Сохранено в файл {filename}")

def save_as_image(canvas):
    if not state["current_client"]:
        messagebox.showwarning("Нет клиента", "Сначала задай имя клиента.")
        return
    filename = filedialog.asksaveasfilename(defaultextension=".png",
        filetypes=[("PNG файлы", "*.png")],
        initialfile=f"{state['current_client']}.png")
    if not filename:
        return
    canvas.postscript(file="tmp_export.eps")
    img = Image.open("tmp_export.eps")
    img.save(filename)
    os.remove("tmp_export.eps")
    messagebox.showinfo("PNG", f"Сохранено как {filename}")

def load_last_client():
    name = state["settings"].get("last_client")
    if not name:
        return
    path = os.path.join(CLIENTS_FOLDER, f"{name}.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        state["figures"] = data.get("figures", [])
        state["connections"] = data.get("connections", [])
        state["current_client"] = name
