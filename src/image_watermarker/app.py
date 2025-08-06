"""
Image Watermarker by srkdesign
"""

import importlib.metadata
import sys
import os

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QLabel, QProgressBar, QMessageBox, QLineEdit, QFormLayout
)
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QFont
from image_watermarker.watermarker import Watermarker

def get_resource_path(relative_path):
    """Return absolute path to resource, works for dev and bundled apps."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

FONT_PATH = get_resource_path(os.path.join("fonts", "PPNeueMontreal-Medium.otf"))

class WatermarkerWorker(QThread):
  progress = Signal(int, int, str)
  finished = Signal()

  def __init__(self, input_folder, output_folder, text, font_size, opacity, margin_x, margin_y):
    super().__init__()
    self.input_folder = input_folder
    self.output_folder = output_folder
    self.text = text
    self.font_size = font_size
    self.opacity = opacity
    self.margin_x = margin_x
    self.margin_y = margin_y

  def run(self):
    try:
      watermarker = Watermarker(
        font_path=FONT_PATH, 
        text=self.text,
        font_size=self.font_size,
        opacity=self.opacity,
        margin_x=self.margin_x,
        margin_y=self.margin_y,
      )

      watermarker.apply_watermark(
        input_folder=self.input_folder,
        output_folder=self.output_folder,
        progress_callback = lambda current, total, name: self.progress.emit(current, total, name)
      )
    except Exception as e:
      print(f"Error: {e}")
    finally:
      self.finished.emit()

class MainWindow(QMainWindow):
  def __init__(self):
    super().__init__()
    self.init_ui()

  def init_ui(self):
    self.setWindowTitle("Image Watermarker by srkdesign")
    self.setMinimumSize(800, 600)

    self.input_folder = ""
    self.output_folder = ""

    central_widget = QWidget(self)
    self.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)

    self.input_label = QLabel("Input Folder: Not selected")
    self.input_label.setWordWrap(True)
    self.input_btn = QPushButton("Select Input Folder")
    self.input_btn.clicked.connect(self.select_input_folder)

    self.output_label = QLabel("Output Folder: Not selected")
    self.output_label.setWordWrap(True)
    self.output_btn = QPushButton("Select Output Folder")
    self.output_btn.clicked.connect(self.select_output_folder)

    folder_layout = QVBoxLayout()
    folder_layout.addWidget(self.input_btn)
    folder_layout.addWidget(self.input_label)
    folder_layout.addWidget(self.output_btn)
    folder_layout.addWidget(self.output_label)

    layout.addLayout(folder_layout)

    form_layout = QFormLayout()
    self.text_input = QLineEdit("© srkdesign")
    self.font_size_input = QLineEdit("72")
    self.opacity_input = QLineEdit("120")
    self.margin_x_input = QLineEdit("25")
    self.margin_y_input = QLineEdit("-75")

    form_layout.addRow("Watermark Text:", self.text_input)
    form_layout.addRow("Font Size:", self.font_size_input)
    form_layout.addRow("Opacity (0-255):", self.opacity_input)
    form_layout.addRow("Margin X:", self.margin_x_input)
    form_layout.addRow("Margin Y:", self.margin_y_input)

    layout.addLayout(form_layout)

    # --- Run & Status ---
    self.run_btn = QPushButton("Start Watermarking")
    self.run_btn.setEnabled(False)
    self.run_btn.clicked.connect(self.start_watermarking)

    self.status_label = QLabel("Status: Waiting")
    self.progress_bar = QProgressBar()

    layout.addWidget(self.run_btn)
    layout.addWidget(self.status_label)
    layout.addWidget(self.progress_bar)

  def select_input_folder(self):
    folder = QFileDialog.getExistingDirectory(self, "Select Input Folder")
    if folder:
        self.input_folder = folder
        self.input_label.setText(f"Input Folder: {folder}")
        self.check_ready()

  def select_output_folder(self):
    folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
    if folder:
        self.output_folder = folder
        self.output_label.setText(f"Output Folder: {folder}")
        self.check_ready()

  def check_ready(self):
    if self.input_folder and self.output_folder:
      self.run_btn.setEnabled(True)

  def start_watermarking(self):
    self.status_label.setText("Processing...")
    self.progress_bar.setValue(0)

    try:
      text = self.text_input.text().strip()
      font_size = int(self.font_size_input.text())
      opacity = int(self.opacity_input.text())
      margin_x = int(self.margin_x_input.text())
      margin_y = int(self.margin_y_input.text())

      if not (0 <= opacity <= 255):
        raise ValueError("Opacity must be between 0 and 255")
    except ValueError as e:
      QMessageBox.warning(self, "Invalid Input", str(e))
      return

    self.worker = WatermarkerWorker(
      input_folder=self.input_folder,
      output_folder=self.output_folder,
      text=text,
      font_size=font_size,
      opacity=opacity,
      margin_x=margin_x,
      margin_y=margin_y
    )

    self.worker.progress.connect(self.update_progress)
    self.worker.finished.connect(self.finish)
    self.worker.start()

  def update_progress(self, current, total, filename):
    self.progress_bar.setMaximum(total)
    self.progress_bar.setValue(current)
    self.status_label.setText(f"Processing {filename} ({current}/{total})")

  def finish(self):
    self.status_label.setText("Done!")
    self.run_btn.setEnabled(True)

def main():
    # Linux desktop environments use an app's .desktop file to integrate the app
    # in to their application menus. The .desktop file of this app will include
    # the StartupWMClass key, set to app's formal name. This helps associate the
    # app's windows to its menu item.
    #
    # For association to work, any windows of the app must have WMCLASS property
    # set to match the value set in app's desktop file. For PySide6, this is set
    # with setApplicationName().

    # Find the name of the module that was used to start the app
    app_module = sys.modules["__main__"].__package__
    # Retrieve the app's metadata
    metadata = importlib.metadata.metadata(app_module)

    QApplication.setApplicationName(metadata["Formal-Name"])

    app = QApplication(sys.argv)
    font = QFont()
    font.setPointSize(16)
    app.setFont(font)
    app.setStyleSheet("""
      QLineEdit {
          padding: 4px;
      }
      QPushButton {
        height: 20px;
      }
    """)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
