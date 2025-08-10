from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
import sys, os

from parameter_items import ParameterItems
from simulation_widget import SimulationWidget
from ui_manager import UIManager

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    items = ParameterItems()
    ex = SimulationWidget(items)

    ui_manager = UIManager()
    ui_manager.apply_theme(ex)
    ex.show()
    sys.exit(app.exec())
