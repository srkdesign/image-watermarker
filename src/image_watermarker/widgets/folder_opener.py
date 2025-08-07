from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QSizePolicy
import sys
import os

class FolderOpener(QWidget):
  def __init__(self, label, folder_path="", parent=None):
    super().__init__(parent)

    self.label = label
    self.folder_path = folder_path

    layout = QVBoxLayout(self)
    layout.setContentsMargins(0, 0, 0, 0)

    self.btn = QPushButton(label)
    self.btn.clicked.connect(self.open_folder)

    self.btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    layout.addWidget(self.btn)

  def set_folder_path(self, folder_path):
    self.folder_path = folder_path

  def open_folder(self):
    if os.path.isdir(self.folder_path):
      QDesktopServices.openUrl(QUrl.fromLocalFile(self.folder_path))
    else:
      print(f"Folder doesn't exist: {self.folder_path}")
