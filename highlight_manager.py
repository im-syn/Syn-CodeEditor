import os
import json

HIGHLIGHT_DIR = os.path.join(os.getcwd(), 'configs', 'highlight')
HIGHLIGHT_PATH = os.path.join(HIGHLIGHT_DIR, 'syntx_highlight.json')

LANG_ROOT = os.path.join(os.getcwd(), 'data', 'languages')
MANIFEST_PATH = os.path.join(LANG_ROOT, 'manifest.json')

DEFAULT_HIGHLIGHT = {
    "python": {
        "keyword": "#82aaff",
        "string": "#c3e88d",
        "comment": "#676e95",
        "function": "#ffcb6b",
        "variable": "#f78c6c",
        "number": "#f78c6c",
        "builtin": "#b2ccd6"
    },
    "php": {
        "keyword": "#ff5370",
        "string": "#c3e88d",
        "comment": "#546e7a",
        "function": "#82aaff",
        "variable": "#f78c6c",
        "number": "#f78c6c",
        "builtin": "#b2ccd6"
    }
}

def ensure_highlight_json():
    os.makedirs(HIGHLIGHT_DIR, exist_ok=True)
    if not os.path.exists(HIGHLIGHT_PATH):
        with open(HIGHLIGHT_PATH, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_HIGHLIGHT, f, indent=2)
    # Ensure LANG_ROOT and at least python folder and demo files
    os.makedirs(LANG_ROOT, exist_ok=True)
    python_dir = os.path.join(LANG_ROOT, 'python')
    os.makedirs(python_dir, exist_ok=True)
    # Demo files for python
    demo_files = {
        "keywords.json": [
            {"word": "def", "comment": "Function definition"},
            {"word": "class", "comment": "Class definition"},
            {"word": "import", "comment": "Import statement"}
        ],
        "functions.json": [
            {"word": "print", "comment": "Print to stdout"},
            {"word": "len", "comment": "Get length"}
        ],
        "imports.json": [
            {"word": "os", "comment": "OS module"},
            {"word": "sys", "comment": "System module"}
        ]
    }
    for fname, content in demo_files.items():
        fpath = os.path.join(python_dir, fname)
        if not os.path.exists(fpath):
            with open(fpath, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2)

def get_highlight_rules(lang):
    ensure_highlight_json()
    with open(HIGHLIGHT_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get(lang, data.get('python'))

def get_language_data(lang):
    ensure_highlight_json()
    lang_dir = os.path.join(LANG_ROOT, lang)
    data = {}
    for fname in ["keywords.json", "functions.json", "imports.json"]:
        fpath = os.path.join(lang_dir, fname)
        if os.path.exists(fpath):
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    items = json.load(f)
                    # Accept list of dicts or list of strings
                    data[fname[:-5]] = [item["word"] if isinstance(item, dict) and "word" in item else item for item in items]
            except Exception:
                data[fname[:-5]] = []
        else:
            data[fname[:-5]] = []
    return data  # keys: 'keywords', 'functions', 'imports'

def get_ext_lang_map():
    ensure_highlight_json()
    if os.path.exists(MANIFEST_PATH):
        try:
            with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {} 