import os
import json

CONFIG_DIR = os.path.join(os.getcwd(), 'configs')
SETTINGS_PATH = os.path.join(CONFIG_DIR, 'settings.json')
THEMES_PATH = os.path.join(CONFIG_DIR, 'themes.json')

DEFAULT_SETTINGS = {
    "rounded_borders": True,
    "current_theme": "dark_default",
    "show_line_numbers": True,
    "font_size": 13,
    "font_family": "Fira Mono"
}

DEFAULT_THEMES = [
    {
        "id": "dark_default",
        "name": "Dark Default",
        "styleType": "dark",
        "colors": {
            "background": "#181c20",
            "header": "#23272e",
            "text": "#e0e0e0",
            "accent": "#82aaff",
            "panel": "#20242a",
            "selected": "#2d313a",
            "border": "#23272e",
            "error": "#ff5c5c"
        },
        "ui": {
            "tab_bg": "#23272e",
            "tab_text": "#e0e0e0",
            "tab_selected_bg": "#181c20",
            "tab_selected_text": "#fff",
            "tab_hover_bg": "#2d313a",
            "tab_border": "#23272e",
            "tab_close_icon": "#ff5c5c",
            "sidebar_bg": "#20242a",
            "sidebar_text": "#e0e0e0",
            "sidebar_selected_bg": "#2d313a",
            "toolbar_bg": "#23272e",
            "toolbar_text": "#e0e0e0",
            "toolbar_icon": "#82aaff",
            "line_number_bg": "#20242a",
            "line_number_text": "#676e95",
            "current_line_bg": "#23272e",
            "editor_bg": "#181c20",
            "editor_text": "#e0e0e0"
        },
        "font": {
            "family": "Fira Mono",
            "size": 13,
            "customPath": None
        }
    }
]

def ensure_configs():
    os.makedirs(CONFIG_DIR, exist_ok=True)
    if not os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_SETTINGS, f, indent=2)
    if not os.path.exists(THEMES_PATH):
        with open(THEMES_PATH, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_THEMES, f, indent=2)

def load_settings():
    with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_settings(settings):
    with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=2)

def load_themes():
    with open(THEMES_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_themes(themes):
    with open(THEMES_PATH, 'w', encoding='utf-8') as f:
        json.dump(themes, f, indent=2) 