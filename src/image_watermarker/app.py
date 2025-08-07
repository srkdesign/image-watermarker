"""
Image Watermarker by srkdesign
"""

import importlib.metadata
import sys
from importlib.resources import files

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QProgressBar, QMessageBox, QVBoxLayout, QScrollArea,
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QIcon, QFont
from PySide6.QtWidgets import QSizePolicy

from image_watermarker.watermarker import Watermarker
from image_watermarker.widgets.folder_selector import FolderSelector
from image_watermarker.widgets.option import OptionField
from image_watermarker.widgets.folder_opener import FolderOpener

ICON_PATH = files("image_watermarker.resources").joinpath("icon.png")
FONT_PATH = files("image_watermarker.resources").joinpath("fonts/PPNeueMontreal-Medium.otf")

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
    self.setWindowIcon(QIcon(str(ICON_PATH)))
    self.setMinimumSize(800, 600)

    self.input_folder = ""
    self.output_folder = ""

    central = QWidget(self)
    self.setCentralWidget(central)
    layout = QVBoxLayout(central)
    layout.setAlignment(Qt.AlignJustify)
    layout.setSpacing(8)

    self.input_folder_selector = FolderSelector(
      title="Input Folder",
      dialog_title="Input Folder",
      on_folder_selected=self.on_input_folder_selected,
    )
    self.output_folder_selector = FolderSelector(
      title="Output Folder",
      dialog_title="Output Folder",
      on_folder_selected=self.on_output_folder_selected,
    )

    folder_row = QVBoxLayout()
    folder_row.setSpacing(4)
    folder_row.setAlignment(Qt.AlignTop)
    folder_row.addWidget(self.input_folder_selector)
    folder_row.addWidget(self.output_folder_selector)

    layout.addLayout(folder_row)

    self.text_input = OptionField(label="Текст", default_value="© srkdesign")
    self.font_size_input = OptionField(label="Размер шрифта", default_value="72", is_integer=True)
    self.opacity_input = OptionField(label="Прозрачность (0-255)", default_value="120", is_integer=True, has_max_value=True)
    self.margin_x_input = OptionField(label="Горизонтальный отступ", default_value="25", is_integer=True)
    self.margin_y_input = OptionField(label="Вертикальный отступ", default_value="-75", is_integer=True)

    self.scroll_area = QScrollArea()
    self.scroll_area.setWidgetResizable(True)
    self.scroll_area.setAlignment(Qt.AlignTop)

    self.settings_container = QWidget()
    self.settings_layout = QVBoxLayout(self.settings_container)
    self.settings_layout.setAlignment(Qt.AlignTop)
    self.settings_layout.setSpacing(0)

    self.settings_layout.addWidget(self.text_input)
    self.settings_layout.addWidget(self.font_size_input)
    self.settings_layout.addWidget(self.opacity_input)
    self.settings_layout.addWidget(self.margin_x_input)
    self.settings_layout.addWidget(self.margin_y_input)

    self.scroll_area.setWidget(self.settings_container)
    layout.addWidget(self.scroll_area)

    btn_row = QVBoxLayout()
    btn_row.setSpacing(8)

    self.run_btn = QPushButton("Добавить водяной знак")
    self.run_btn.setEnabled(False)
    self.run_btn.clicked.connect(self.start_watermarking)
    self.run_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    
    self.show_results_btn = FolderOpener(label="Показать результат", folder_path=self.output_folder)
    self.show_results_btn.setEnabled(False)
    self.show_results_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    btn_row.addWidget(self.run_btn)
    btn_row.addWidget(self.show_results_btn)
    layout.addLayout(btn_row)

    self.status_label = QLabel("Статус: В ожидании")
    self.progress_bar = QProgressBar()

    progress_layout = QHBoxLayout()
    progress_layout.setSpacing(16)
    progress_layout.setAlignment(Qt.AlignVCenter)
    progress_layout.addWidget(self.status_label, alignment=Qt.AlignmentFlag.AlignHCenter)
    progress_layout.addWidget(self.progress_bar, stretch=1)

    layout.addLayout(progress_layout)

  def on_input_folder_selected(self, folder):
    self.input_folder = folder
    self.check_ready()

  def on_output_folder_selected(self, folder):
    self.output_folder = folder
    self.show_results_btn.set_folder_path(folder)
    self.check_ready()

  def check_ready(self):
    if self.input_folder and self.output_folder:
      self.run_btn.setEnabled(True)
      self.show_results_btn.setEnabled(True)

  def start_watermarking(self):
    self.status_label.setText("Обработка...")
    self.progress_bar.setValue(0)

    try:
      text = self.text_input.get_text().strip()
      font_size = int(self.font_size_input.get_text())
      opacity = int(self.opacity_input.get_text())
      margin_x = int(self.margin_x_input.get_text())
      margin_y = int(self.margin_y_input.get_text())

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
    self.status_label.setText("Готово!")
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
