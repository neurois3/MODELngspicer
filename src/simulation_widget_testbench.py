from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
import sys, os

from parameter_dictionary import ParameterDictionary
from simulation_widget import SimulationWidget
from ui_manager import UIManager

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    parameter_dictionary = ParameterDictionary()
    ex = SimulationWidget(parameter_dictionary)

    ui_manager = UIManager()
    ui_manager.apply_theme(ex)
    ex.show()
    sys.exit(app.exec())
