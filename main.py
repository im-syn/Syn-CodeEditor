import sys
from PyQt6.QtWidgets import QApplication
from editor.ui.main_window import MainWindow
import config_manager
import highlight_manager

if __name__ == '__main__':
    highlight_manager.ensure_highlight_json()
    config_manager.ensure_configs()
    settings = config_manager.load_settings()
    themes = config_manager.load_themes()
    app = QApplication(sys.argv)
    window = MainWindow(settings=settings, themes=themes)
    window.show()
    sys.exit(app.exec()) 