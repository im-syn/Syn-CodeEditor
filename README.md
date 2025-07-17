# Syn-CodeEditor

**Syn-CodeEditor** is a modern, extensible, and beautiful code editor built with Python and PyQt6. It features advanced syntax highlighting, a powerful file explorer, tabbed editing, customizable themes, and a robust configuration system. Designed for developers who want a fast, visually appealing, and highly configurable desktop code editor.

---
<img width="1851" height="1210" alt="image" src="https://github.com/user-attachments/assets/d5a2f351-3a02-4c88-a028-eb33d7faa00f" />
<img width="1850" height="1219" alt="image" src="https://github.com/user-attachments/assets/041177c9-4bee-48c9-ab9e-35e561084ce8" />

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Themes & UI Customization](#themes--ui-customization)
- [Syntax Highlighting](#syntax-highlighting)
- [Extending Language Support](#extending-language-support)
- [Keyboard Shortcuts](#keyboard-shortcuts)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- **Modern UI**: Frameless, rounded, and themeable window with a custom title bar and toolbar.
- **Tabbed Editing**: Open and edit multiple files in tabs, with unsaved changes indicator.
- **File Explorer**: Sidebar file tree with context menu (copy, cut, paste, move, delete, rename, new file/folder, undo).
- **Advanced Syntax Highlighting**: Customizable per-language highlighting, easily extensible.
- **Themes**: Switch between light and dark themes, or add your own.
- **Settings Panel**: Change font, theme, line numbers, and more from a GUI panel.
- **Undo for File Operations**: Undo create, delete, move, and rename actions in the file explorer.
- **Keyboard Shortcuts**: Common shortcuts like Ctrl+S (save), Ctrl+O (open), Ctrl+Z (undo), and more.
- **Cross-Platform**: Runs on Windows, Linux, and macOS (PyQt6).

---

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/im-syn/Syn-CodeEditor.git
   cd Syn-CodeEditor/codeEdtior
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

4. **Build an executable (Windows .exe) with PyInstaller:**
   
   First, install PyInstaller if you haven't already:
   ```bash
   pip install pyinstaller
   ```
   Then, from the `codeEdtior` directory, run:
   ```bash
   pyinstaller --noconfirm --onefile --windowed --add-data "configs;configs" --add-data "data;data" --name Syn-CodeEditor main.py
   ```
   - The `--windowed` flag prevents a console window from appearing.
   - The `--add-data` options ensure your `configs` and `data` folders are bundled.
   - The output `.exe` will be in the `dist/` folder.
   
   For more advanced options or troubleshooting, see the [PyInstaller documentation](https://pyinstaller.org/).

---

## Getting Started

- On first launch, Syn-CodeEditor will create default configuration and highlighting files in the `configs/` and `data/` directories.
- Use the sidebar to open folders and files. Double-click files to open them in tabs.
- Access the settings panel via the sidebar to customize your experience.

---

## Project Structure

```
codeEdtior/
  ├── main.py                # Entry point
  ├── requirements.txt       # Python dependencies
  ├── config_manager.py      # Loads/saves user settings and themes
  ├── highlight_manager.py   # Loads/saves syntax highlighting rules and language data
  ├── configs/
  │   ├── settings.json      # User settings (font, theme, etc.)
  │   ├── themes.json        # Theme definitions
  │   └── highlight/
  │       └── syntx_highlight.json # Syntax highlight color rules
  ├── data/
  │   └── languages/
  │       └── python/
  │           ├── keywords.json
  │           ├── functions.json
  │           └── imports.json
  └── editor/
      └── ui/
          ├── main_window.py # Main window, layout, and logic
          ├── code_editor.py # Editor widget, syntax highlighting
          ├── file_tree.py   # File explorer sidebar
          ├── tabs.py        # Tabbed editing
          ├── toolbar.py     # Toolbar (open/save)
          └── title_bar.py   # Custom title bar
```

---

## Configuration

All user settings are stored in `configs/settings.json`. You can edit this file directly or use the built-in settings panel.

Example settings:
```json
{
  "rounded_borders": true,
  "current_theme": "dark_default",
  "show_line_numbers": true,
  "font_size": 15,
  "font_family": "Source Code Pro"
}
```

- **rounded_borders**: Enable/disable rounded window corners.
- **current_theme**: Theme ID from `themes.json`.
- **show_line_numbers**: Show/hide line numbers in the editor.
- **font_size**: Editor font size.
- **font_family**: Editor font family.

---

## Themes & UI Customization

Themes are defined in `configs/themes.json`. Each theme includes colors for UI elements and editor, as well as font settings.

Example theme:
```json
{
  "id": "dark_default",
  "name": "Dark Default",
  "styleType": "dark",
  "colors": { ... },
  "ui": { ... },
  "font": {
    "family": "Fira Mono",
    "size": 13
  }
}
```

- Switch themes from the settings panel or with the sidebar theme button.
- Add your own themes by editing `themes.json`.

---

## Syntax Highlighting

Syn-CodeEditor uses a powerful, extensible syntax highlighting system:

- Highlighting rules are defined in `configs/highlight/syntx_highlight.json`:
  ```json
  {
    "python": {
      "keyword": "#82aaff",
      "string": "#c3e88d",
      "comment": "#676e95",
      "function": "#ffcb6b",
      "variable": "#f78c6c",
      "number": "#f78c6c",
      "builtin": "#b2ccd6"
    }
  }
  ```
- You can add or modify colors for any supported language.

### How Highlighting Works

- The editor detects the language based on file extension.
- For each language, it loads:
  - **Keywords** (`data/languages/python/keywords.json`)
  - **Functions** (`data/languages/python/functions.json`)
  - **Imports** (`data/languages/python/imports.json`)
- The `highlight_manager.py` module loads these rules and provides them to the editor.
- The `CustomHighlighter` class in `code_editor.py` applies the rules using Qt's `QSyntaxHighlighter`.

---

## Extending Language Support

To add or improve support for a new language:

1. **Add highlight colors** to `configs/highlight/syntx_highlight.json`:
   ```json
   "javascript": {
     "keyword": "#ffb300",
     "string": "#c3e88d",
     ...
   }
   ```
2. **Create a folder** in `data/languages/` (e.g., `javascript/`).
3. **Add language data files**:
   - `keywords.json`
   - `functions.json`
   - `imports.json`
4. **(Optional)** Add an extension-to-language mapping in `data/languages/manifest.json`:
   ```json
   { ".js": "javascript", ".py": "python" }
   ```

---

## Keyboard Shortcuts

- **Ctrl+O**: Open file
- **Ctrl+S**: Save file
- **Ctrl+Shift+S**: Save file as
- **Ctrl+Z**: Undo (in file explorer and editor)
- **Ctrl+Plus/Minus/0**: Zoom in/out/reset editor font
- **Ctrl+W**: Close tab (via context menu)
- **Right-click tab**: Tab context menu (close, close others, copy path, reveal in explorer)

---

## Contributing

Contributions are welcome! To add features, fix bugs, or improve documentation:

1. Fork the repo and create a branch.
2. Make your changes.
3. Submit a pull request.

For language support, see [Extending Language Support](#extending-language-support).

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

**Syn-CodeEditor** — A modern, beautiful, and extensible code editor for everyone. 
