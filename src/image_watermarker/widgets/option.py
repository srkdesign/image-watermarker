from PySide6.QtCore import Signal, QRegularExpression
from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QHBoxLayout
from PySide6.QtGui import QIntValidator, QRegularExpressionValidator

class OptionField(QWidget):
  changed = Signal(float)
  def __init__(self, label="Настройка:", default_value="0", is_integer=False,has_max_value=False, parent=None):
    super().__init__(parent)

    self.input = QLineEdit(default_value)
    self.is_integer = is_integer

    if is_integer:
      if has_max_value:
        validator = QRegularExpressionValidator(QRegularExpression(r"^(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)$"))
      else:
        validator = QIntValidator()
      
      self.input.setValidator(validator)

    layout = QHBoxLayout()
    layout.addWidget(QLabel(f"{label}:"), stretch=1)
    layout.addWidget(self.input, stretch=1)
    self.setLayout(layout)

  def get_text(self):
    return self.input.text()
