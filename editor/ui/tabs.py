from PyQt6.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QMenu, QFileDialog, QApplication, QTabBar
from PyQt6.QtGui import QAction, QFont, QPainter, QColor, QMouseEvent
from PyQt6.QtCore import Qt, QPoint, QRect
import os
import subprocess

class CustomTabBar(QTabBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self._hovered_tab = -1

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        for i in range(self.count()):
            rect = self.tabRect(i)
            x = rect.right() - 22
            y = rect.top() + (rect.height() - 16) // 2
            close_rect = QRect(x, y, 16, 16)
            # Draw X
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setPen(QColor('#ff5c5c'))
            painter.setFont(self.font())
            painter.drawText(close_rect, Qt.AlignmentFlag.AlignCenter, '✕')

    def mouseReleaseEvent(self, event: QMouseEvent):
        for i in range(self.count()):
            rect = self.tabRect(i)
            x = rect.right() - 22
            y = rect.top() + (rect.height() - 16) // 2
            close_rect = QRect(x, y, 16, 16)
            if close_rect.contains(event.pos()):
                self.parent().tabCloseRequested.emit(i)
                return
        super().mouseReleaseEvent(event)

class EditorTabs(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabBar(CustomTabBar(self))
        self.setTabsClosable(False)  # We'll handle close button manually
        self.tabCloseRequested.connect(self.close_tab)
        self.setMovable(True)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        # Remove setStyleSheet here; theming is handled in apply_theme only

    def add_editor_tab(self, widget: QWidget, title: str):
        idx = self.addTab(widget, title)
        self.setCurrentWidget(widget)
        # Connect to text changes to track modifications
        if hasattr(widget, 'editor') and hasattr(widget.editor, 'textChanged'):
            widget.editor.textChanged.connect(lambda w=widget: self.update_tab_title(w))
        widget._tab_index = idx
        # Apply current theme to tabs after adding
        if hasattr(self, 'apply_theme') and hasattr(self.parent(), 'get_current_theme'):
            theme = self.parent().get_current_theme()
            if theme:
                colors = theme.get('colors', {})
                font = theme.get('font', {})
                self.apply_theme(colors, font)

    def update_tab_title(self, editor_widget):
        """Update tab title to show modified indicator"""
        if not hasattr(editor_widget, 'is_modified'):
            return
        
        for i in range(self.count()):
            if self.widget(i) == editor_widget:
                base_title = os.path.basename(editor_widget.file_path) if editor_widget.file_path else "Untitled"
                if editor_widget.is_modified():
                    title = f"{base_title} [*]"
                else:
                    title = base_title
                self.setTabText(i, title)
                break

    def update_all_tab_titles(self):
        """Update all tab titles based on modification state"""
        for i in range(self.count()):
            widget = self.widget(i)
            if hasattr(widget, 'is_modified') and hasattr(widget, 'file_path'):
                base_title = os.path.basename(widget.file_path) if widget.file_path else "Untitled"
                if widget.is_modified():
                    title = f"{base_title} [*]"
                else:
                    title = base_title
                self.setTabText(i, title)

    def _close_icon(self):
        # Unicode X icon
        from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setPen(QColor('#ff5c5c'))
        painter.setFont(self.font())
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, '✕')
        painter.end()
        return QIcon(pixmap)

    def close_tab(self, index):
        widget = self.widget(index)
        self.removeTab(index)
        widget.deleteLater()

    def show_context_menu(self, pos: QPoint):
        tab_index = self.tabBar().tabAt(pos)
        if tab_index == -1:
            return
        menu = QMenu(self)
        menu.setStyleSheet('QMenu { background: #23272e; color: #e0e0e0; font-size: 14px; } QMenu::item:selected { background: #2d313a; }')
        close_action = QAction('Close', self)
        close_action.triggered.connect(lambda: self.close_tab(tab_index))
        close_others_action = QAction('Close Others', self)
        close_others_action.triggered.connect(lambda: self.close_others(tab_index))
        close_all_action = QAction('Close All', self)
        close_all_action.triggered.connect(self.close_all)
        copy_path_action = QAction('Copy Path', self)
        copy_path_action.triggered.connect(lambda: self.copy_path(tab_index))
        reveal_explorer_action = QAction('Reveal in Explorer', self)
        reveal_explorer_action.triggered.connect(lambda: self.reveal_in_explorer(tab_index))
        menu.addAction(close_action)
        menu.addAction(close_others_action)
        menu.addAction(close_all_action)
        menu.addSeparator()
        menu.addAction(copy_path_action)
        menu.addAction(reveal_explorer_action)
        menu.exec(self.tabBar().mapToGlobal(pos))

    def close_others(self, index):
        for i in reversed(range(self.count())):
            if i != index:
                self.close_tab(i)

    def close_all(self):
        for i in reversed(range(self.count())):
            self.close_tab(i)

    def copy_path(self, index):
        widget = self.widget(index)
        if hasattr(widget, 'file_path'):
            QApplication.clipboard().setText(widget.file_path)

    def reveal_in_explorer(self, index):
        widget = self.widget(index)
        if hasattr(widget, 'file_path'):
            path = widget.file_path
            if os.name == 'nt':
                subprocess.Popen(f'explorer /select,"{path}"')
            else:
                subprocess.Popen(['xdg-open', os.path.dirname(path)])

    def apply_theme(self, colors, font, ui=None):
        ui = ui or {}
        bg = ui.get('tab_bg', colors.get('header', '#23272e'))
        text = ui.get('tab_text', colors.get('text', '#23272e'))
        selected = ui.get('tab_selected_bg', colors.get('background', '#181c20'))
        selected_text = ui.get('tab_selected_text', '#fff')
        hover = ui.get('tab_hover_bg', colors.get('selected', '#2d313a'))
        border = ui.get('tab_border', colors.get('border', '#23272e'))
        close_icon = ui.get('tab_close_icon', '#ff5c5c')
        self.setStyleSheet(f'''
            QTabWidget::pane {{
                border: none;
                background: {bg};
            }}
            QTabBar::tab {{
                background: {bg};
                color: {text};
                border-radius: 8px 8px 0 0;
                padding: 8px 22px 8px 18px;
                margin-right: 2px;
                font-size: 15px;
                min-width: 80px;
                transition: background 0.2s;
            }}
            QTabBar::tab:selected {{
                background: {selected};
                color: {selected_text};
            }}
            QTabBar::tab:hover {{
                background: {hover};
            }}
        ''')
        font_family = font.get('family', 'Fira Mono')
        font_size = font.get('size', 13)
        font_obj = QFont(font_family, font_size)
        self.tabBar().setFont(font_obj)
        # Propagate to tab widgets
        for i in range(self.count()):
            widget = self.widget(i)
            if hasattr(widget, 'apply_theme'):
                widget.apply_theme(colors, font, ui)
        # Set close icon color for custom tab bar
        if hasattr(self.tabBar(), 'set_close_icon_color'):
            self.tabBar().set_close_icon_color(close_icon) 