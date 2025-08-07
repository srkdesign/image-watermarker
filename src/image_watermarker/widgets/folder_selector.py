from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QPushButton, QFileDialog
from PySide6.QtCore import Qt

class FolderSelector(QWidget):
  def __init__(self, title, dialog_title, on_folder_selected=None, parent=None):
    super().__init__(parent)

    self.folder_path = ""

    self.dialog_title = dialog_title

    self.label = QLabel(title)
    self.label.setWordWrap(True)

    self.on_folder_selected = on_folder_selected

    self.btn = QPushButton(f"Выбрать {title}")
    self.btn.clicked.connect(self.select_folder)

    self.layout = QHBoxLayout(self)
    self.layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignVCenter)
    self.layout.addWidget(self.btn)

  def select_folder(self):
    folder = QFileDialog.getExistingDirectory(self, self.dialog_title)
    if folder:
      self.folder_path = folder
      self.label.setText(f"{self.dialog_title}: {folder}")

      if self.on_folder_selected:
        self.on_folder_selected(folder)

  def get_folder(self):
    return self.folder_path