import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QSplitter,
    QFileDialog, QFrame, QSizePolicy, QHBoxLayout, QPushButton, QStackedWidget,
    QLabel, QVBoxLayout, QLineEdit, QCheckBox, QSpinBox, QDoubleSpinBox, QHBoxLayout, QPushButton, QScrollArea, QWidget, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt, QRect, QRectF
from PyQt6.QtGui import QPainterPath, QRegion, QIcon
from .title_bar import TitleBar
from .toolbar import EditorToolBar
from .tabs import EditorTabs
from .file_tree import FileTree
from .code_editor import CodeEditor
from config_manager import save_settings, load_settings, DEFAULT_SETTINGS

class SettingsPanel(QWidget):
    def __init__(self, settings, themes, main_window, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.themes = themes
        self.main_window = main_window
        self.widgets = {}
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText('Search settings...')
        self.search_box.textChanged.connect(self.update_filter)
        self.layout.addWidget(self.search_box)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll)
        self.build_settings_ui()
        # Save and Reset buttons
        btn_row = QHBoxLayout()
        self.save_btn = QPushButton('Save')
        self.save_btn.clicked.connect(self.save_settings)
        btn_row.addWidget(self.save_btn)
        self.reset_btn = QPushButton('Reset to Default')
        self.reset_btn.clicked.connect(self.reset_to_default)
        btn_row.addWidget(self.reset_btn)
        self.layout.addLayout(btn_row)

    def build_settings_ui(self):
        from PyQt6.QtWidgets import QComboBox
        # Remove old widgets
        for i in reversed(range(self.scroll_layout.count())):
            item = self.scroll_layout.takeAt(i)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.widgets.clear()
        # Font and theme options
        font_options = [
            'Fira Mono', 'Consolas', 'JetBrains Mono', 'Source Code Pro',
            'Menlo', 'Monaco', 'Ubuntu Mono', 'Cascadia Mono', 'Courier New'
        ]
        theme_options = [t['id'] for t in self.themes]
        for key, value in self.settings.items():
            row = QHBoxLayout()
            label = QLabel(key.replace('_', ' ').capitalize())
            label.setMinimumWidth(140)
            row.addWidget(label)
            if key == 'font_family':
                widget = QComboBox()
                widget.addItems(font_options)
                if value in font_options:
                    widget.setCurrentText(value)
                widget.currentTextChanged.connect(lambda v, k=key: self.update_setting(k, v))
            elif key == 'current_theme':
                widget = QComboBox()
                widget.addItems(theme_options)
                if value in theme_options:
                    widget.setCurrentText(value)
                widget.currentTextChanged.connect(self.on_theme_changed)
            elif isinstance(value, bool):
                widget = QCheckBox()
                widget.setChecked(value)
                widget.stateChanged.connect(lambda state, k=key: self.update_setting(k, bool(state)))
            elif isinstance(value, int):
                widget = QSpinBox()
                widget.setValue(value)
                widget.valueChanged.connect(lambda v, k=key: self.update_setting(k, v))
            elif isinstance(value, float):
                widget = QDoubleSpinBox()
                widget.setValue(value)
                widget.valueChanged.connect(lambda v, k=key: self.update_setting(k, v))
            else:
                widget = QLineEdit(str(value))
                widget.textChanged.connect(lambda v, k=key: self.update_setting(k, v))
            widget.setObjectName(key)
            row.addWidget(widget)
            self.widgets[key] = (label, widget, row)
            self.scroll_layout.addLayout(row)
        self.scroll_layout.addStretch()

    def on_theme_changed(self, theme_id):
        self.settings['current_theme'] = theme_id
        save_settings(self.settings)
        for t in self.themes:
            if t['id'] == theme_id:
                self.main_window.apply_theme(t)
                self.main_window.file_tree.apply_theme(t.get('colors', {}), t.get('font', {}))
                self.main_window.tabs.apply_theme(t.get('colors', {}), t.get('font', {}))
                if self.main_window.centralWidget():
                    bg = t.get('colors', {}).get('background', '#181c20')
                    self.main_window.centralWidget().setStyleSheet(f'background: {bg}; border-radius: {self.main_window.RADIUS if self.settings.get("rounded_borders", True) else 0}px;')
                break

    def update_setting(self, key, value):
        self.settings[key] = value

    def save_settings(self):
        save_settings(self.settings)

    def reset_to_default(self):
        reply = QMessageBox.question(self, 'Reset Settings', 'Are you sure you want to reset all settings to default?', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.settings.clear()
            self.settings.update(DEFAULT_SETTINGS)
            self.build_settings_ui()
            save_settings(self.settings)

    def update_filter(self, text):
        text = text.lower()
        for key, (label, widget, row) in self.widgets.items():
            visible = text in key.lower() or text in label.text().lower()
            label.setVisible(visible)
            widget.setVisible(visible)
            for i in range(row.count()):
                item = row.itemAt(i)
                if item.widget():
                    item.widget().setVisible(visible)

    def apply_theme(self, colors, font, ui=None):
        ui = ui or {}
        bg = ui.get('background', colors.get('background', '#181c20'))
        text = ui.get('text', colors.get('text', '#e0e0e0'))
        self.setStyleSheet(f'background: {bg}; color: {text};')
        for key, (label, widget, _) in self.widgets.items():
            label.setStyleSheet(f'color: {text};')
            widget.setStyleSheet(f'color: {text}; background: {bg};')
        self.search_box.setStyleSheet(f"background: {bg}; color: {text}; border: 1px solid {ui.get('border', '#23272e')}; border-radius: 6px; padding: 4px;")

class MainWindow(QMainWindow):
    RESIZE_MARGIN = 12  # Increased for easier corner grabbing
    RADIUS = 16

    def __init__(self, settings=None, themes=None):
        super().__init__()
        self.settings = settings or {}
        self.themes = themes or []
        self.setWindowTitle('Modern Python Code Editor')
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.resize(1200, 800)
        self.setMinimumSize(900, 600)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setStyleSheet('border-radius: 16px; background: transparent;')

        # ─── Central + main layout ────────────────────────────────────────────────
        central = QWidget()
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ─── Header: TitleBar + Toolbar ──────────────────────────────────────────
        self.header = QWidget()
        self.header.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )
        header_layout = QVBoxLayout(self.header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)
        self.title_bar = TitleBar(self)
        header_layout.addWidget(self.title_bar)
        self.toolbar = EditorToolBar(self)
        self.toolbar.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )
        self.toolbar.openFileClicked.connect(self.open_file_dialog)
        self.toolbar.openFolderClicked.connect(self.open_folder_dialog)
        self.toolbar.saveClicked.connect(self.save_current_file)
        self.toolbar.saveFileClicked.connect(self.save_current_file_as)  # Connect new signal
        header_layout.addWidget(self.toolbar)
        self.header.setStyleSheet(
            'background: #181c20; '
            'border-top-left-radius: 16px; border-top-right-radius: 16px;'
            'border-bottom: 2px solid #23272e;'
        )
        main_layout.addWidget(self.header, stretch=0)

        # ─── Main area: sidebar + file‐tree/tabs/settings ────────────────────────
        main_area = QFrame()
        main_area.setFrameShape(QFrame.Shape.NoFrame)
        main_area.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        main_area_layout = QHBoxLayout(main_area)
        main_area_layout.setContentsMargins(0, 0, 0, 0)
        main_area_layout.setSpacing(0)

        # Sidebar (vertical)
        self.sidebar = QWidget()
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        self.files_btn = QPushButton()
        self.files_btn.setIcon(QIcon.fromTheme('folder'))
        self.files_btn.setToolTip('Files')
        self.files_btn.setCheckable(True)
        self.files_btn.setChecked(True)
        self.files_btn.setFixedSize(40, 40)
        self.files_btn.setStyleSheet('QPushButton { border: none; background: #23272e; } QPushButton:checked { background: #181c20; }')
        self.files_btn.clicked.connect(lambda: self.switch_panel(0))
        sidebar_layout.addWidget(self.files_btn)
        self.settings_btn = QPushButton()
        self.settings_btn.setIcon(QIcon.fromTheme('settings'))
        self.settings_btn.setToolTip('Settings')
        self.settings_btn.setCheckable(True)
        self.settings_btn.setChecked(False)
        self.settings_btn.setFixedSize(40, 40)
        self.settings_btn.setStyleSheet('QPushButton { border: none; background: #23272e; } QPushButton:checked { background: #181c20; }')
        self.settings_btn.clicked.connect(lambda: self.switch_panel(1))
        sidebar_layout.addWidget(self.settings_btn)
        sidebar_layout.addStretch()
        # Theme switch button
        self.theme_switch_btn = QPushButton('🌙')
        self.theme_switch_btn.setToolTip('Switch Light/Dark Theme')
        self.theme_switch_btn.setFixedSize(40, 40)
        self.theme_switch_btn.setStyleSheet('QPushButton { background: #181c20; color: #ffcc80; border: none; border-radius: 8px; font-size: 20px; } QPushButton:hover { background: #23272e; }')
        self.theme_switch_btn.clicked.connect(self.switch_theme)
        sidebar_layout.addWidget(self.theme_switch_btn)
        self.sidebar.setStyleSheet('background: #23272e; border-right: 1px solid #23272e;')
        main_area_layout.addWidget(self.sidebar, stretch=0)

        # Stacked panel: 0 = file tree/tabs, 1 = settings
        self.stacked_panel = QStackedWidget()
        # Panel 0: file tree + tabs
        file_tabs_panel = QWidget()
        file_tabs_layout = QVBoxLayout(file_tabs_panel)
        file_tabs_layout.setContentsMargins(0, 0, 0, 0)
        file_tabs_layout.setSpacing(0)
        splitter = QSplitter()
        root_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../../..')
        )
        self.file_tree = FileTree(root_path)
        self.file_tree.fileOpened.connect(self.open_file_in_tab)
        splitter.addWidget(self.file_tree)
        self.tabs = EditorTabs()
        splitter.addWidget(self.tabs)
        splitter.setSizes([260, 940])
        file_tabs_layout.addWidget(splitter)
        self.stacked_panel.addWidget(file_tabs_panel)
        # Panel 1: settings (placeholder)
        self.settings_panel = SettingsPanel(self.settings, self.themes, self)
        self.stacked_panel.addWidget(self.settings_panel)
        main_area_layout.addWidget(self.stacked_panel, stretch=1)
        main_layout.addWidget(main_area, stretch=1)
        self.setCentralWidget(central)

        # After UI setup, apply theme
        theme = self.get_current_theme()
        if theme:
            self.apply_theme(theme)
            self.file_tree.apply_theme(theme.get('colors', {}), theme.get('font', {}))
            self.tabs.apply_theme(theme.get('colors', {}), theme.get('font', {}))
            # Set central widget background from theme
            bg = theme.get('colors', {}).get('background', '#181c20')
            central.setStyleSheet(f'background: {bg}; border-radius: {self.RADIUS if self.settings.get("rounded_borders", True) else 0}px;')

        # ─── Window resizing & title‐bar signals ─────────────────────────────────
        self._is_maximized = False
        self._is_resizing = False
        self._resize_dir = None
        self.setMouseTracking(True)
        central.setMouseTracking(True)
        self.header.setMouseTracking(True)
        main_area.setMouseTracking(True)
        splitter.setMouseTracking(True)
        self.title_bar.closeClicked.connect(self.close)
        self.title_bar.minimizeClicked.connect(self.showMinimized)
        self.title_bar.maximizeClicked.connect(self.toggle_max_restore)
        self.update_rounded_corners()
        
        # Add keyboard shortcuts
        from PyQt6.QtGui import QShortcut, QKeySequence
        self.ctrl_s_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        self.ctrl_s_shortcut.activated.connect(self.save_current_file)

    def get_current_theme(self):
        theme_id = self.settings.get('current_theme')
        for t in self.themes:
            if t.get('id') == theme_id:
                return t
        return self.themes[0] if self.themes else None

    def apply_theme(self, theme):
        colors = theme.get('colors', {})
        font = theme.get('font', {})
        ui = theme.get('ui', {})
        bg = ui.get('background', colors.get('background', '#181c20'))
        sidebar_bg = ui.get('sidebar_bg', colors.get('panel', '#20242a'))
        border = ui.get('sidebar_border', colors.get('border', '#23272e'))
        header_bg = ui.get('toolbar_bg', colors.get('header', '#23272e'))
        text_color = ui.get('sidebar_text', colors.get('text', '#e0e0e0'))
        accent = colors.get('accent', '#82aaff')
        selected_bg = ui.get('sidebar_selected_bg', colors.get('selected', '#2d313a'))
        radius = self.RADIUS if self.settings.get('rounded_borders', True) else 0

        # Main window background and border radius
        self.setStyleSheet(f'border-radius: {self.RADIUS if self.settings.get("rounded_borders", True) else 0}px; background: transparent;')
        if self.centralWidget():
            self.centralWidget().setStyleSheet(f'background: {bg}; border-radius: {self.RADIUS if self.settings.get("rounded_borders", True) else 0}px;')

        # Sidebar
        if hasattr(self, 'sidebar'):
            self.sidebar.setStyleSheet(f'background: {sidebar_bg}; border-right: 1px solid {border};')
            btn_style = f'''
                QPushButton {{
                    background: {sidebar_bg};
                    color: {text_color};
                    border: none;
                    border-radius: 10px;
                    font-size: 18px;
                    margin: 4px 0;
                }}
                QPushButton:checked {{
                    background: {selected_bg};
                }}
                QPushButton:hover {{
                    background: {selected_bg};
                }}
            '''
            self.files_btn.setStyleSheet(btn_style)
            self.settings_btn.setStyleSheet(btn_style)
            # Theme switch button
            theme_btn_style = f'''
                QPushButton {{
                    background: {sidebar_bg};
                    color: #ffcc80;
                    border: none;
                    border-radius: 10px;
                    font-size: 20px;
                    margin: 4px 0;
                }}
                QPushButton:hover {{
                    background: {selected_bg};
                }}
            '''
            self.theme_switch_btn.setStyleSheet(theme_btn_style)

        # Header (title bar + toolbar)
        if hasattr(self, 'header'):
            self.header.setStyleSheet(
                f'background: {header_bg}; '
                f'border-top-left-radius: {radius}px; border-top-right-radius: {radius}px;'
                f'border-bottom: 2px solid {border};'
            )
        if hasattr(self, 'title_bar') and hasattr(self.title_bar, 'apply_theme'):
            self.title_bar.apply_theme(colors, font, ui)
        if hasattr(self, 'toolbar') and hasattr(self.toolbar, 'apply_theme'):
            self.toolbar.apply_theme(colors, font, ui)

        # File tree
        if hasattr(self, 'file_tree') and hasattr(self.file_tree, 'apply_theme'):
            self.file_tree.apply_theme(colors, font, ui)

        # Tabs
        if hasattr(self, 'tabs') and hasattr(self.tabs, 'apply_theme'):
            self.tabs.apply_theme(colors, font, ui)

        # Code editor (all tabs)
        if hasattr(self, 'tabs'):
            for i in range(self.tabs.count()):
                editor = self.tabs.widget(i)
                if hasattr(editor, 'apply_theme'):
                    editor.apply_theme(colors, font, ui)

        # Settings panel
        if hasattr(self, 'settings_panel') and hasattr(self.settings_panel, 'apply_theme'):
            self.settings_panel.apply_theme(colors, font, ui)

    def get_theme_font(self):
        # Prefer font from settings, else from theme
        font_family = self.settings.get('font_family') or self.get_current_theme().get('font', {}).get('family', 'Fira Mono')
        font_size = self.settings.get('font_size') or self.get_current_theme().get('font', {}).get('size', 13)
        return font_family, font_size

    def switch_panel(self, idx):
        self.stacked_panel.setCurrentIndex(idx)
        self.files_btn.setChecked(idx == 0)
        self.settings_btn.setChecked(idx == 1)

    def resizeEvent(self, event):
        self.update_rounded_corners()
        super().resizeEvent(event)

    def update_rounded_corners(self):
        path = QPainterPath()
        rect = QRectF(0, 0, self.width(), self.height())
        path.addRoundedRect(rect, self.RADIUS, self.RADIUS)
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

    def toggle_max_restore(self):
        if self._is_maximized:
            self.showNormal()
        else:
            self.showMaximized()
        self._is_maximized = not self._is_maximized

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._resize_dir = self._get_resize_direction(event.pos())
            if self._resize_dir:
                self._is_resizing = True
                self._resize_start_pos = event.globalPosition().toPoint()
                self._resize_start_geom = self.geometry()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._is_resizing and self._resize_dir:
            self._resize_window(event.globalPosition().toPoint())
        else:
            self.setCursor(self._get_cursor_shape(event.pos()))
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._is_resizing = False
        self._resize_dir = None
        self.setCursor(Qt.CursorShape.ArrowCursor)
        super().mouseReleaseEvent(event)

    def _get_resize_direction(self, pos):
        rect = self.rect()
        x, y, w, h, m = pos.x(), pos.y(), rect.width(), rect.height(), self.RESIZE_MARGIN
        # Corners first
        if x < m and y < m:
            # print('topleft')
            return 'topleft'
        if x > w - m and y < m:
            # print('topright')
            return 'topright'
        if x < m and y > h - m:
            # print('bottomleft')
            return 'bottomleft'
        if x > w - m and y > h - m:
            # print('bottomright')
            return 'bottomright'
        dirs = []
        if x < m: dirs.append('l')
        if x > w - m: dirs.append('r')
        if y < m: dirs.append('t')
        if y > h - m: dirs.append('b')
        # print('edge:', ''.join(dirs) or None)
        return ''.join(dirs) or None

    def _resize_window(self, global_pos):
        dx = global_pos.x() - self._resize_start_pos.x()
        dy = global_pos.y() - self._resize_start_pos.y()
        geom = self._resize_start_geom
        x, y, w, h = geom.x(), geom.y(), geom.width(), geom.height()
        d = self._resize_dir
        minw, minh = self.minimumWidth(), self.minimumHeight()
        if d == 'topleft':
            new_x = min(x + dx, x + w - minw)
            new_y = min(y + dy, y + h - minh)
            w = max(w - dx, minw)
            h = max(h - dy, minh)
            x = new_x
            y = new_y
        elif d == 'topright':
            new_y = min(y + dy, y + h - minh)
            w = max(w + dx, minw)
            h = max(h - dy, minh)
            y = new_y
        elif d == 'bottomleft':
            new_x = min(x + dx, x + w - minw)
            w = max(w - dx, minw)
            h = max(h + dy, minh)
            x = new_x
        elif d == 'bottomright':
            w = max(w + dx, minw)
            h = max(h + dy, minh)
        else:
            if 'l' in d:
                new_x = min(x + dx, x + w - minw)
                w = max(w - dx, minw)
                x = new_x
            if 'r' in d:
                w = max(w + dx, minw)
            if 't' in d:
                new_y = min(y + dy, y + h - minh)
                h = max(h - dy, minh)
                y = new_y
            if 'b' in d:
                h = max(h + dy, minh)
        self.setGeometry(x, y, w, h)

    def _get_cursor_shape(self, pos):
        d = self._get_resize_direction(pos)
        if d in ('l', 'r'):   return Qt.CursorShape.SizeHorCursor
        if d in ('t', 'b'):   return Qt.CursorShape.SizeVerCursor
        if d in ('topleft','bottomright'):  return Qt.CursorShape.SizeFDiagCursor
        if d in ('topright','bottomleft'):  return Qt.CursorShape.SizeBDiagCursor
        return Qt.CursorShape.ArrowCursor

    def open_file_in_tab(self, file_path):
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == os.path.basename(file_path):
                self.tabs.setCurrentIndex(i)
                return

        editor = CodeEditor()
        # Apply current theme to the new editor before showing
        theme = self.get_current_theme()
        if theme:
            colors = theme.get('colors', {})
            font = theme.get('font', {})
            editor.apply_theme(colors, font)
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            editor.set_file_content(content, file_path)
        except Exception as e:
            editor.set_file_content(f'Error opening file: {e}', file_path)

        self.tabs.add_editor_tab(editor, os.path.basename(file_path))
        # Update tab title to show initial state
        self.tabs.update_tab_title(editor)
        # Apply theme to tabs (in case of theme switch)
        if theme:
            self.tabs.apply_theme(colors, font)

    def open_file_dialog(self):
        fp, _ = QFileDialog.getOpenFileName(self, 'Open File', '', 'All Files (*)')
        if fp:
            self.open_file_in_tab(fp)

    def open_folder_dialog(self):
        folder = QFileDialog.getExistingDirectory(self, 'Open Folder', '')
        if folder:
            self.file_tree.show_tree(folder)

    def save_current_file(self):
        """Save current file (Ctrl+S behavior)"""
        current = self.tabs.currentWidget()
        if current and isinstance(current, CodeEditor):
            if hasattr(current, 'save_file'):
                success = current.save_file()
                if success:
                    self.tabs.update_tab_title(current)
            else:
                # Fallback for older editor instances
                if current.file_path:
                    try:
                        with open(current.file_path, 'w', encoding='utf-8') as f:
                            f.write(current.toPlainText())
                    except Exception:
                        pass

    def save_current_file_as(self):
        """Save current file as (toolbar button behavior)"""
        current = self.tabs.currentWidget()
        if current and isinstance(current, CodeEditor):
            if hasattr(current, 'save_file_as'):
                success = current.save_file_as()
                if success:
                    self.tabs.update_tab_title(current)
            else:
                # Fallback for older editor instances
                fp, _ = QFileDialog.getSaveFileName(self, 'Save File As', '', 'All Files (*)')
                if fp:
                    try:
                        with open(fp, 'w', encoding='utf-8') as f:
                            f.write(current.toPlainText())
                    except Exception:
                        pass

    def switch_theme(self):
        current_theme = self.get_current_theme()
        if not current_theme or not self.themes:
            return
        current_type = current_theme.get('styleType', 'dark')
        # Find next theme of opposite styleType
        next_type = 'light' if current_type == 'dark' else 'dark'
        for t in self.themes:
            if t.get('styleType') == next_type:
                self.settings['current_theme'] = t['id']
                save_settings(self.settings)
                self.apply_theme(t)
                # Update file tree/tabs for new theme
                self.file_tree.apply_theme(t.get('colors', {}), t.get('font', {}))
                self.tabs.apply_theme(t.get('colors', {}), t.get('font', {}))
                # Update theme switch icon
                self.theme_switch_btn.setText('🌙' if next_type == 'dark' else '☀️')
                # Update central widget bg
                if self.centralWidget():
                    bg = t.get('colors', {}).get('background', '#181c20')
                    self.centralWidget().setStyleSheet(f'background: {bg}; border-radius: {self.RADIUS if self.settings.get("rounded_borders", True) else 0}px;')
                return
        # If no opposite type found, cycle to first theme
        t = self.themes[0]
        self.settings['current_theme'] = t['id']
        save_settings(self.settings)
        self.apply_theme(t)
        self.file_tree.apply_theme(t.get('colors', {}), t.get('font', {}))
        self.tabs.apply_theme(t.get('colors', {}), t.get('font', {}))
        self.theme_switch_btn.setText('🌙' if t.get('styleType', 'dark') == 'dark' else '☀️')
        if self.centralWidget():
            bg = t.get('colors', {}).get('background', '#181c20')
            self.centralWidget().setStyleSheet(f'background: {bg}; border-radius: {self.RADIUS if self.settings.get("rounded_borders", True) else 0}px;')
