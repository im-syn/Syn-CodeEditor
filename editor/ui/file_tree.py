import os
from PyQt6.QtWidgets import QTreeView, QVBoxLayout, QWidget, QLabel, QPushButton, QFileDialog, QMenu, QInputDialog, QApplication
from PyQt6.QtGui import QFileSystemModel, QIcon, QAction, QFont
from PyQt6.QtCore import pyqtSignal, Qt, QPoint, QFileSystemWatcher
import shutil

class FileTree(QWidget):
    fileOpened = pyqtSignal(str)
    folderOpened = pyqtSignal(str)

    def __init__(self, root_path=None, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.model = None
        self.tree = None
        self.empty_panel = None
        self.current_folder = root_path
        self.clipboard_path = None
        self.clipboard_cut = False
        self.undo_stack = []  # (op, details)
        self.fs_watcher = QFileSystemWatcher()
        self.fs_watcher.directoryChanged.connect(self.on_dir_changed)
        if root_path:
            self.show_tree(root_path)
        else:
            self.show_empty_panel()

    def keyPressEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Z:
            self.undo_last_action()
            event.accept()
        else:
            super().keyPressEvent(event)

    def undo_last_action(self):
        if not self.undo_stack:
            return
        op, details = self.undo_stack.pop()
        try:
            if op == 'delete':
                # Restore file/folder from backup
                src, backup = details['path'], details['backup']
                if os.path.isdir(backup):
                    shutil.move(backup, src)
                else:
                    shutil.move(backup, src)
            elif op == 'rename':
                os.rename(details['new'], details['old'])
            elif op == 'create':
                # Remove the created file/folder
                if os.path.isdir(details['path']):
                    shutil.rmtree(details['path'])
                else:
                    os.remove(details['path'])
            elif op == 'move':
                shutil.move(details['dst'], details['src'])
        except Exception:
            pass
        if self.model and self.current_folder:
            self.model.setRootPath(self.current_folder)

    def show_tree(self, folder_path):
        self.clear_layout()
        self.model = QFileSystemModel()
        self.model.setRootPath(folder_path)
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(folder_path))
        self.tree.setColumnHidden(1, True)  # Hide size
        self.tree.setColumnHidden(2, True)  # Hide type
        self.tree.setColumnHidden(3, True)  # Hide date
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(18)
        self.tree.setAnimated(True)
        self.tree.setExpandsOnDoubleClick(True)
        self.tree.setStyleSheet('''
            QTreeView {
                background: #20242a;
                color: #e0e0e0;
                border: none;
                font-size: 15px;
                padding: 8px 0 8px 0;
            }
            QTreeView::item {
                padding: 6px 8px;
                margin: 2px 0;
            }
            QTreeView::item:selected {
                background: #2d313a;
                color: #fff;
                border-radius: 6px;
            }
        ''')
        self.tree.setColumnWidth(0, 220)
        self.tree.clicked.connect(self.on_item_clicked)
        self.tree.setToolTipDuration(3000)
        self.tree.setMouseTracking(True)
        self.tree.entered.connect(self.on_item_hovered)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        self.layout.addWidget(self.tree)
        self.fs_watcher.removePaths(self.fs_watcher.directories())
        self.fs_watcher.addPath(folder_path)
        self.current_folder = folder_path
        self.folderOpened.emit(folder_path)

    def show_empty_panel(self):
        self.clear_layout()
        self.empty_panel = QWidget()
        panel_layout = QVBoxLayout(self.empty_panel)
        panel_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label = QLabel("<h2>No folder open</h2><p>Click below to open a folder and start exploring your project.</p>")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        open_btn = QPushButton("Open Folder")
        open_btn.setFixedWidth(160)
        open_btn.setStyleSheet('font-size: 16px; padding: 10px; background: #23272e; color: #fff; border-radius: 8px;')
        open_btn.clicked.connect(self.open_folder_dialog)
        panel_layout.addWidget(label)
        panel_layout.addWidget(open_btn)
        self.layout.addStretch()
        self.layout.addWidget(self.empty_panel)
        self.layout.addStretch()
        self.current_folder = None

    def open_folder_dialog(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'Open Folder', '')
        if folder_path:
            self.show_tree(folder_path)

    def clear_layout(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def on_item_clicked(self, index):
        file_path = self.model.filePath(index)
        if os.path.isfile(file_path):
            self.fileOpened.emit(file_path)

    def on_item_hovered(self, index):
        if not index.isValid():
            self.tree.setToolTip("")
            return
        info = self.model.fileInfo(index)
        size = info.size()
        date = info.lastModified().toString('yyyy-MM-dd hh:mm')
        type_ = "Folder" if info.isDir() else info.suffix() or "File"
        tooltip = f"<b>{info.fileName()}</b><br>Type: {type_}<br>Size: {size} bytes<br>Modified: {date}"
        self.tree.setToolTip(tooltip)

    def show_context_menu(self, pos: QPoint):
        index = self.tree.indexAt(pos)
        menu = QMenu(self)
        menu.setStyleSheet('QMenu { background: #23272e; color: #e0e0e0; font-size: 14px; } QMenu::item:selected { background: #2d313a; }')
        file_path = self.model.filePath(index) if index.isValid() else None
        is_dir = os.path.isdir(file_path) if file_path else False
        has_selection = index.isValid()
        # Determine target dir for new file/folder
        if file_path is None:
            target_dir = self.current_folder
        else:
            target_dir = file_path if is_dir else os.path.dirname(file_path)
        # Copy
        copy_action = QAction('Copy', self)
        copy_action.setEnabled(has_selection)
        copy_action.triggered.connect(lambda: self.copy_path(file_path, cut=False))
        menu.addAction(copy_action)
        # Cut
        cut_action = QAction('Cut', self)
        cut_action.setEnabled(has_selection)
        cut_action.triggered.connect(lambda: self.copy_path(file_path, cut=True))
        menu.addAction(cut_action)
        # Paste
        paste_action = QAction('Paste', self)
        paste_action.setEnabled(self.clipboard_path is not None and (is_dir or not has_selection))
        paste_action.triggered.connect(lambda: self.paste_path(file_path if is_dir else os.path.dirname(file_path) if file_path else self.current_folder))
        menu.addAction(paste_action)
        menu.addSeparator()
        # Move
        move_action = QAction('Move...', self)
        move_action.setEnabled(has_selection)
        move_action.triggered.connect(lambda: self.move_item(file_path))
        menu.addAction(move_action)
        # Delete
        delete_action = QAction('Delete', self)
        delete_action.setEnabled(has_selection)
        delete_action.triggered.connect(lambda: self.delete_item(file_path, index))
        menu.addAction(delete_action)
        # Rename
        rename_action = QAction('Rename', self)
        rename_action.setEnabled(has_selection)
        rename_action.triggered.connect(lambda: self.rename_item(file_path, index))
        menu.addAction(rename_action)
        menu.addSeparator()
        # New File
        new_file_action = QAction('New File', self)
        new_file_action.setEnabled(target_dir is not None)
        new_file_action.triggered.connect(lambda: self.create_new_file(target_dir))
        menu.addAction(new_file_action)
        # New Folder
        new_folder_action = QAction('New Folder', self)
        new_folder_action.setEnabled(target_dir is not None)
        new_folder_action.triggered.connect(lambda: self.create_new_folder(target_dir))
        menu.addAction(new_folder_action)
        menu.exec(self.tree.viewport().mapToGlobal(pos))

    def copy_path(self, file_path, cut=False):
        self.clipboard_path = file_path
        self.clipboard_cut = cut
        QApplication.clipboard().setText(file_path)

    def paste_path(self, dest_dir):
        if not self.clipboard_path or not dest_dir:
            return
        base_name = os.path.basename(self.clipboard_path)
        dest_path = os.path.join(dest_dir, base_name)
        if os.path.exists(dest_path):
            return  # Don't overwrite
        try:
            if os.path.isdir(self.clipboard_path):
                if self.clipboard_cut:
                    shutil.move(self.clipboard_path, dest_path)
                else:
                    shutil.copytree(self.clipboard_path, dest_path)
            else:
                if self.clipboard_cut:
                    shutil.move(self.clipboard_path, dest_path)
                else:
                    shutil.copy2(self.clipboard_path, dest_path)
            if self.clipboard_cut:
                self.clipboard_path = None
                self.clipboard_cut = False
        except Exception:
            pass
        if self.model and self.current_folder:
            self.model.setRootPath(self.current_folder)

    def move_item(self, file_path):
        if not file_path:
            return
        dest_dir = QFileDialog.getExistingDirectory(self, 'Move to Folder', os.path.dirname(file_path))
        if dest_dir:
            base_name = os.path.basename(file_path)
            dest_path = os.path.join(dest_dir, base_name)
            try:
                shutil.move(file_path, dest_path)
                self.undo_stack.append(('move', {'src': file_path, 'dst': dest_path}))
            except Exception:
                pass
            if self.model and self.current_folder:
                self.model.setRootPath(self.current_folder)

    def create_new_file(self, dir_path):
        # Always use self.current_folder if dir_path is None
        if not dir_path:
            dir_path = self.current_folder
        if not dir_path:
            return
        name, ok = QInputDialog.getText(self, 'New File', 'Enter file name:')
        if ok and name:
            file_path = os.path.join(dir_path, name)
            if not os.path.exists(file_path):
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write('')
                    self.undo_stack.append(('create', {'path': file_path}))
                except Exception:
                    pass
            if self.model and self.current_folder:
                self.model.setRootPath(self.current_folder)

    def create_new_folder(self, dir_path):
        # Always use self.current_folder if dir_path is None
        if not dir_path:
            dir_path = self.current_folder
        if not dir_path:
            return
        name, ok = QInputDialog.getText(self, 'New Folder', 'Enter folder name:')
        if ok and name:
            folder_path = os.path.join(dir_path, name)
            if not os.path.exists(folder_path):
                try:
                    os.makedirs(folder_path)
                    self.undo_stack.append(('create', {'path': folder_path}))
                except Exception:
                    pass
            if self.model and self.current_folder:
                self.model.setRootPath(self.current_folder)

    def delete_item(self, file_path, index):
        # Move to temp backup for undo
        import tempfile
        backup = tempfile.mktemp(prefix='deleted_', dir=tempfile.gettempdir())
        try:
            if os.path.isdir(file_path):
                shutil.move(file_path, backup)
            else:
                shutil.move(file_path, backup)
            self.undo_stack.append(('delete', {'path': file_path, 'backup': backup}))
        except Exception:
            pass
        self.model.remove(index)

    def rename_item(self, file_path, index):
        base_dir = os.path.dirname(file_path)
        old_name = os.path.basename(file_path)
        new_name, ok = QInputDialog.getText(self, 'Rename', 'Enter new name:', text=old_name)
        if ok and new_name and new_name != old_name:
            new_path = os.path.join(base_dir, new_name)
            try:
                os.rename(file_path, new_path)
                self.model.setData(index, new_name)
                self.undo_stack.append(('rename', {'old': file_path, 'new': new_path}))
            except Exception as e:
                pass

    def apply_theme(self, colors, font, ui=None):
        ui = ui or {}
        bg = ui.get('sidebar_bg', colors.get('panel', '#20242a'))
        text = ui.get('sidebar_text', colors.get('text', '#e0e0e0'))
        selected = ui.get('sidebar_selected_bg', colors.get('selected', '#2d313a'))
        border = ui.get('sidebar_border', colors.get('border', '#23272e'))
        self.setStyleSheet(f'background: {bg}; color: {text};')
        font_family = font.get('family', 'Fira Mono')
        font_size = font.get('size', 13)
        font_obj = QFont(font_family, font_size)
        if self.tree:
            self.tree.setStyleSheet(f'''
                QTreeView {{
                    background: {bg};
                    color: {text};
                    border: none;
                    font-size: 15px;
                    padding: 8px 0 8px 0;
                }}
                QTreeView::item {{
                    padding: 6px 8px;
                    margin: 2px 0;
                }}
                QTreeView::item:selected {{
                    background: {selected};
                    color: #fff;
                    border-radius: 6px;
                }}
            ''')
            self.tree.setFont(font_obj)
        if self.empty_panel:
            self.empty_panel.setStyleSheet(f'background: {bg}; color: {text};')

    def on_dir_changed(self, path):
        if self.model and self.current_folder:
            self.model.setRootPath(self.current_folder) 