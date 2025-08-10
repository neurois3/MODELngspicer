from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
import sys, os

from ui_manager import UIManager
from exponential_spin_box import ExponentialSpinBox
from parameter_items import ParameterItems
from parameter_table import ParameterTable

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    # Create an instance of ParameterItems
    items = ParameterItems()
    items.set_value('a', 3.42E+03)
    items.set_value('b', 9.87E-02)
    items.set_value('c', 1.00E+00)

    # Create an instance of ParameterTable
    ex = ParameterTable(items)
    ex.display()

    ui_manager = UIManager()
    ui_manager.apply_theme(ex)
    ex.show()
    sys.exit(app.exec())
