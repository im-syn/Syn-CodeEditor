from highlight_manager import get_highlight_rules, get_language_data, get_ext_lang_map
from PyQt6.QtWidgets import QPlainTextEdit, QWidget, QVBoxLayout, QTextEdit, QLabel
from PyQt6.QtGui import QFont, QColor, QSyntaxHighlighter, QTextCharFormat, QPainter
from PyQt6.QtCore import QRegularExpression, QRect, QSize, Qt
import os

def detect_language(file_path):
    ext_lang_map = get_ext_lang_map()
    ext = os.path.splitext(file_path or '')[1].lower()
    return ext_lang_map.get(ext, 'python')

class CustomHighlighter(QSyntaxHighlighter):
    def __init__(self, document, rules, lang_data=None):
        super().__init__(document)
        self.rules = rules or {}
        self.lang_data = lang_data or {}
        self.highlighting_rules = []
        # Keywords
        if 'keyword' in self.rules:
            keyword_format = QTextCharFormat()
            keyword_format.setForeground(QColor(self.rules['keyword']))
            keyword_format.setFontWeight(QFont.Weight.Bold)
            # Built-in + user keywords
            keywords = [
                'and', 'as', 'assert', 'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
                'False', 'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'None',
                'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'True', 'try', 'while', 'with', 'yield'
            ]
            keywords += self.lang_data.get('keywords', [])
            for word in set(keywords):
                pattern = QRegularExpression(rf'\\b{word}\\b')
                self.highlighting_rules.append((pattern, keyword_format))
        # Strings
        if 'string' in self.rules:
            string_format = QTextCharFormat()
            string_format.setForeground(QColor(self.rules['string']))
            self.highlighting_rules.append((QRegularExpression(r'".*?"'), string_format))
            self.highlighting_rules.append((QRegularExpression(r"'.*?"), string_format))
            self.highlighting_rules.append((QRegularExpression(r'`.*?`'), string_format))
        # Comments
        if 'comment' in self.rules:
            comment_format = QTextCharFormat()
            comment_format.setForeground(QColor(self.rules['comment']))
            self.highlighting_rules.append((QRegularExpression(r'#.*'), comment_format))
            self.highlighting_rules.append((QRegularExpression(r'//.*'), comment_format))
        # Numbers
        if 'number' in self.rules:
            number_format = QTextCharFormat()
            number_format.setForeground(QColor(self.rules['number']))
            self.highlighting_rules.append((QRegularExpression(r'\b[0-9]+\b'), number_format))
        # Functions (word followed by '(')
        if 'function' in self.rules:
            func_format = QTextCharFormat()
            func_format.setForeground(QColor(self.rules['function']))
            func_format.setFontItalic(True)
            # Built-in + user functions
            functions = self.lang_data.get('functions', [])
            for word in set(functions):
                pattern = QRegularExpression(rf'\\b{word}\\b(?=\s*\()')
                self.highlighting_rules.append((pattern, func_format))
            # fallback: any word before (
            self.highlighting_rules.append((QRegularExpression(r'\b\w+(?=\s*\()'), func_format))
        # Imports (for import/include/require)
        if 'import' in self.rules:
            import_format = QTextCharFormat()
            import_format.setForeground(QColor(self.rules['import']))
            imports = self.lang_data.get('imports', [])
            for word in set(imports):
                pattern = QRegularExpression(rf'\\b{word}\\b')
                self.highlighting_rules.append((pattern, import_format))
        # Variables (word before =)
        if 'variable' in self.rules:
            var_format = QTextCharFormat()
            var_format.setForeground(QColor(self.rules['variable']))
            self.highlighting_rules.append((QRegularExpression(r'\b\w+(?=\s*=)'), var_format))
        # Builtins (for python)
        if 'builtin' in self.rules:
            builtin_format = QTextCharFormat()
            builtin_format.setForeground(QColor(self.rules['builtin']))
            builtins = ['print', 'len', 'range', 'str', 'int', 'float', 'list', 'dict', 'set', 'tuple', 'open']
            for word in builtins:
                pattern = QRegularExpression(rf'\\b{word}\\b')
                self.highlighting_rules.append((pattern, builtin_format))

    def highlightBlock(self, text):
        for pattern, fmt in self.highlighting_rules:
            it = pattern.globalMatch(text)
            while it.hasNext():
                match = it.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self):
        return QSize(self.code_editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.code_editor.line_number_area_paint_event(event)

class CodeEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.empty_state = QLabel("<div style='text-align:center; color:#676e95; font-size:22px; margin-top:60px;'>🗒️<br><b>No file open</b><br><span style='font-size:15px;'>Open a file to start editing!</span></div>")
        self.empty_state.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.editor = _CodeEditorWidget()
        self.editor.hide()
        self.layout.addWidget(self.empty_state)
        self.layout.addWidget(self.editor)
        self.file_path = None
        self.original_content = None
        self.modified = False
        self.show_empty_state()
        self._base_font_size = 13
        self._font_family = 'Fira Mono'
        self._zoom = 0
        
        # Connect text changes to track modifications
        self.editor.textChanged.connect(self.on_text_changed)

    def set_file_content(self, content, file_path=None):
        self.file_path = file_path
        if file_path is not None:
            self.editor.setPlainText(content if content is not None else '')
            self.original_content = content if content is not None else ''
            self.modified = False
            self.editor.show()
            self.empty_state.hide()
            # Set highlighter based on file extension
            lang = detect_language(file_path)
            rules = get_highlight_rules(lang)
            lang_data = get_language_data(lang)
            self.editor.set_highlighter(rules, lang_data)
        else:
            self.editor.clear()
            self.editor.hide()
            self.empty_state.show()
            self.original_content = None
            self.modified = False

    def wheelEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)

    def keyPressEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if event.key() in (Qt.Key.Key_Plus, Qt.Key.Key_Equal):
                self.zoom_in()
                event.accept()
                return
            elif event.key() == Qt.Key.Key_Minus:
                self.zoom_out()
                event.accept()
                return
            elif event.key() == Qt.Key.Key_0:
                self.reset_zoom()
                event.accept()
                return
        super().keyPressEvent(event)

    def zoom_in(self):
        self._zoom += 1
        self.update_font()

    def zoom_out(self):
        self._zoom -= 1
        self.update_font()

    def reset_zoom(self):
        self._zoom = 0
        self.update_font()

    def update_font(self):
        size = max(6, self._base_font_size + self._zoom)
        font = QFont(self._font_family, size)
        self.editor.setFont(font)
        self.editor.setStyleSheet(f"font-size: {size}px;")

    def clear_editor(self):
        self.set_file_content('', None)

    def show_empty_state(self):
        self.editor.hide()
        self.empty_state.show()

    def show_editor(self):
        self.empty_state.hide()
        self.editor.show()

    def toPlainText(self):
        return self.editor.toPlainText()

    def setPlainText(self, text):
        self.set_file_content(text)

    def on_text_changed(self):
        """Track when text has been modified"""
        if self.file_path is not None:
            current_content = self.editor.toPlainText()
            self.modified = (current_content != self.original_content)

    def is_modified(self):
        """Check if the file has been modified"""
        return self.modified

    def save_file(self, force_save_as=False):
        """Save the current file content"""
        if self.file_path is None:
            return self.save_file_as()
        
        if force_save_as:
            return self.save_file_as()
        
        try:
            content = self.editor.toPlainText()
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.original_content = content
            self.modified = False
            return True
        except Exception as e:
            print(f"Error saving file: {e}")
            return False

    def save_file_as(self):
        """Save file with a new path"""
        from PyQt6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getSaveFileName(self, 'Save File As', '', 'All Files (*)')
        if file_path:
            try:
                content = self.editor.toPlainText()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.file_path = file_path
                self.original_content = content
                self.modified = False
                return True
            except Exception as e:
                print(f"Error saving file: {e}")
                return False
        return False

    def apply_theme(self, colors, font, ui=None):
        ui = ui or {}
        bg = ui.get('editor_bg', colors.get('background', '#181c20'))
        text = ui.get('editor_text', colors.get('text', '#e0e0e0'))
        panel = ui.get('line_number_bg', colors.get('panel', '#20242a'))
        selected = ui.get('current_line_bg', colors.get('selected', '#2d313a'))
        line_number_text = ui.get('line_number_text', '#676e95')
        font_family = font.get('family', 'Fira Mono')
        font_size = font.get('size', 13)
        self.setStyleSheet(f'background: {bg}; color: {text};')
        self.empty_state.setStyleSheet(f'color: #676e95; background: {bg}; font-size:22px;')
        if hasattr(self, 'editor') and hasattr(self.editor, 'apply_theme'):
            self.editor.apply_theme(colors, font, panel, selected, line_number_text, bg, text)

class _CodeEditorWidget(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self._panel_color = '#20242a'
        self._selected_color = '#23272e'
        self._line_number_color = '#676e95'
        self.setFont(QFont('Fira Mono', 13))
        self.setStyleSheet('''
            QPlainTextEdit {
                background: #181c20;
                color: #e0e0e0;
                border: none;
                padding: 12px 0 12px 0;
                font-family: 'Fira Mono', 'Consolas', 'Monaco', monospace;
            }
        ''')
        self.highlighter = None
        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.update_line_number_area_width(0)
        self.highlight_current_line()

    def set_highlighter(self, rules, lang_data=None):
        if self.highlighter:
            self.highlighter.setDocument(None)
        self.highlighter = CustomHighlighter(self.document(), rules, lang_data)

    def line_number_area_width(self):
        digits = len(str(max(1, self.blockCount())))
        return 18 + self.fontMetrics().horizontalAdvance('9') * digits

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor(self._panel_color))
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor(self._line_number_color))
                painter.drawText(0, top, self.line_number_area.width() - 4, self.fontMetrics().height(), Qt.AlignmentFlag.AlignRight, number)
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1

    def highlight_current_line(self):
        extra_selections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(QColor(self._selected_color))
            selection.format.setProperty(QTextCharFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            extra_selections.append(selection)
        self.setExtraSelections(extra_selections)

    def apply_theme(self, colors, font, panel=None, selected=None, line_number_text=None, editor_bg=None, editor_text=None):
        bg = editor_bg or colors.get('background', '#181c20')
        text = editor_text or colors.get('text', '#e0e0e0')
        panel = panel or colors.get('panel', '#20242a')
        selected = selected or colors.get('selected', '#2d313a')
        line_number_text = line_number_text or '#676e95'
        font_family = font.get('family', 'Fira Mono')
        font_size = font.get('size', 13)
        self.setFont(QFont(font_family, font_size))
        self.setStyleSheet(f'''
            QPlainTextEdit {{
                background: {bg};
                color: {text};
                border: none;
                padding: 12px 0 12px 0;
                font-family: '{font_family}', 'Consolas', 'Monaco', monospace;
            }}
        ''')
        self._panel_color = panel
        self._selected_color = selected
        self._line_number_color = line_number_text
        if hasattr(self, 'line_number_area'):
            self.line_number_area.setStyleSheet(f'background: {panel};')
        self.highlight_current_line() 