##модуль 2 из 6: config.py 📁
##Он отвечает за загрузку и сохранение:
##настроек (settings.json)
##фраз (phrases.json)
##инициализацию дефолтов, если что-то отсутствует

import os
import json
from model import state

SETTINGS_FILE = "settings.json"
PHRASES_FILE = "phrases.json"

DEFAULTS = {
    "use_images": True,
    "grid": True,
    "show_labels": True,
    "default_font": {
        "family": "Arial",
        "size": 12,
        "color": "#000000"
    },
    "default_connection": {
        "width": 2,
        "color": "#000000",
        "style": "arrow"
    },
    "last_client": None
}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            state["settings"] = json.load(f)
        # Добавляем недостающие поля
        for key, val in DEFAULTS.items():
            if key not in state["settings"]:
                state["settings"][key] = val
    else:
        state["settings"] = DEFAULTS.copy()

def save_settings():
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(state["settings"], f, indent=2, ensure_ascii=False)

def load_phrases():
    if os.path.exists(PHRASES_FILE):
        with open(PHRASES_FILE, "r", encoding="utf-8") as f:
            state["phrases"] = json.load(f)
    else:
        state["phrases"] = {"фигуры": [], "связи": []}
