from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
from typing import override
import sys, os

from ui_theme import apply_theme
from exponential_spin_box import ExponentialSpinBox

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex  = ExponentialSpinBox()
    apply_theme(ex)
    ex.show()
    sys.exit(app.exec())
