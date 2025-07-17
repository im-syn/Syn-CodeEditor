from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont

class TitleBar(QWidget):
    closeClicked = pyqtSignal()
    minimizeClicked = pyqtSignal()
    maximizeClicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(32)
        self.setStyleSheet('''
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #23272e, stop:1 #181c20);
            color: white;
            border-bottom: 1px solid #23272e;
        ''')
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 0, 6, 0)
        layout.setSpacing(6)

        # App icon (placeholder)
        self.icon = QLabel()
        pixmap = QPixmap(20, 20)
        pixmap.fill(Qt.GlobalColor.transparent)
        self.icon.setPixmap(pixmap)
        self.icon.setStyleSheet('background: #3a3f4b; border-radius: 4px; min-width: 20px; min-height: 20px;')
        layout.addWidget(self.icon)

        self.title = QLabel('Modern Python Code Editor')
        self.title.setStyleSheet('font-weight: bold; font-size: 14px; margin-left: 6px;')
        layout.addWidget(self.title)
        layout.addStretch()

        btn_style = 'QPushButton { background: none; color: white; font-size: 14px; border: none; min-width: 22px; min-height: 22px; border-radius: 4px; } QPushButton:hover { background: #2d313a; }'
        self.min_btn = QPushButton('-')
        self.min_btn.setStyleSheet(btn_style)
        self.min_btn.clicked.connect(self.minimizeClicked.emit)
        layout.addWidget(self.min_btn)

        self.max_btn = QPushButton('[]')
        self.max_btn.setStyleSheet(btn_style)
        self.max_btn.clicked.connect(self.maximizeClicked.emit)
        layout.addWidget(self.max_btn)

        self.close_btn = QPushButton('X')
        self.close_btn.setStyleSheet(btn_style + ' QPushButton { color: #ff5c5c; } QPushButton:hover { background: #3a2323; }')
        self.close_btn.clicked.connect(self.closeClicked.emit)
        layout.addWidget(self.close_btn)

        self.setLayout(layout)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()
            self._dragging = True
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if hasattr(self, '_dragging') and self._dragging:
            parent = self.window()
            if parent:
                diff = event.globalPosition().toPoint() - self._drag_pos
                parent.move(parent.pos() + diff)
                self._drag_pos = event.globalPosition().toPoint()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._dragging = False
        super().mouseReleaseEvent(event)

    def apply_theme(self, colors, font, ui=None):
        ui = ui or {}
        bg = ui.get('toolbar_bg', colors.get('header', '#23272e'))
        bg2 = ui.get('background', colors.get('background', '#181c20'))
        text = ui.get('toolbar_text', colors.get('text', '#e0e0e0'))
        border = ui.get('toolbar_border', colors.get('border', '#23272e'))
        accent = ui.get('toolbar_icon', colors.get('accent', '#82aaff'))
        self.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {bg2}, stop:1 {bg});
            color: {text};
            border-bottom: 1px solid {border};
        """)
        self.title.setStyleSheet(f'font-weight: bold; font-size: 14px; margin-left: 6px; color: {text};')
        btn_style = f'''
            QPushButton {{ background: none; color: {text}; font-size: 14px; border: none; min-width: 22px; min-height: 22px; border-radius: 4px; }}
            QPushButton:hover {{ background: {ui.get('tab_hover_bg', '#2d313a')}; }}
        '''
        self.min_btn.setStyleSheet(btn_style)
        self.max_btn.setStyleSheet(btn_style)
        self.close_btn.setStyleSheet(
            btn_style + f" QPushButton {{ color: {ui.get('tab_close_icon', '#ff5c5c')}; }} QPushButton:hover {{ background: #3a2323; }}"
        )
        font_family = font.get('family', 'Fira Mono')
        font_size = font.get('size', 13)
        font_obj = QFont(font_family, font_size)
        self.title.setFont(font_obj)
        for btn in [self.min_btn, self.max_btn, self.close_btn]:
            btn.setFont(font_obj) 