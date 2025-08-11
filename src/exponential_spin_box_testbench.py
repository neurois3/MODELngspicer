from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
from typing import override
import sys, os

from ui_manager import UIManager
from exponential_spin_box import ExponentialSpinBox

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex  = ExponentialSpinBox()

    ui_manager = UIManager()
    ui_manager.apply_theme(ex)
    ex.show()
    sys.exit(app.exec())
