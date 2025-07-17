from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont

class EditorToolBar(QWidget):
    openFileClicked = pyqtSignal()
    openFolderClicked = pyqtSignal()
    saveClicked = pyqtSignal()
    saveFileClicked = pyqtSignal()  # New signal for toolbar save button

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 0, 6, 0)
        layout.setSpacing(8)

        btn_style = '''
            QPushButton {
                background: #23272e;
                color: #e0e0e0;
                font-size: 13px;
                border: none;
                border-radius: 4px;
                padding: 4px 10px;
                min-width: 28px;
            }
            QPushButton:hover {
                background: #2d313a;
                color: #fff;
            }
            QPushButton:pressed {
                background: #181c20;
            }
        '''
        self.open_file_btn = QPushButton('\U0001F4C4  Open File')
        self.open_file_btn.setStyleSheet(btn_style)
        self.open_file_btn.clicked.connect(self.openFileClicked.emit)
        layout.addWidget(self.open_file_btn)

        self.open_folder_btn = QPushButton('\U0001F4C1  Open Folder')
        self.open_folder_btn.setStyleSheet(btn_style)
        self.open_folder_btn.clicked.connect(self.openFolderClicked.emit)
        layout.addWidget(self.open_folder_btn)

        self.save_btn = QPushButton('\U0001F4BE  Save')
        self.save_btn.setStyleSheet(btn_style)
        self.save_btn.clicked.connect(self.saveFileClicked.emit)  # Changed to saveFileClicked
        layout.addWidget(self.save_btn)

        layout.addStretch()
        self.setLayout(layout)

    def apply_theme(self, colors, font, ui=None):
        ui = ui or {}
        bg = ui.get('toolbar_bg', colors.get('header', '#23272e'))
        text = ui.get('toolbar_text', colors.get('text', '#e0e0e0'))
        hover = ui.get('tab_hover_bg', colors.get('selected', '#2d313a'))
        pressed = ui.get('toolbar_bg', colors.get('background', '#181c20'))
        btn_style = f'''
            QPushButton {{
                background: {bg};
                color: {text};
                font-size: 13px;
                border: none;
                border-radius: 4px;
                padding: 4px 10px;
                min-width: 28px;
            }}
            QPushButton:hover {{
                background: {hover};
                color: #fff;
            }}
            QPushButton:pressed {{
                background: {pressed};
            }}
        '''
        font_family = font.get('family', 'Fira Mono')
        font_size = font.get('size', 13)
        font_obj = QFont(font_family, font_size)
        for btn in [self.open_file_btn, self.open_folder_btn, self.save_btn]:
            btn.setStyleSheet(btn_style)
            btn.setFont(font_obj)
        self.setStyleSheet(f'background: {bg};') 