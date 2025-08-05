from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
import sys, os

from parameter_items import ParameterItems
from simulation_widget import SimulationWidget
from ui_theme import apply_theme

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    items = ParameterItems()
    ex = SimulationWidget(items)
    apply_theme(ex)
    ex.show()
    sys.exit(app.exec())
