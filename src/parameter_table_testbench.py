from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
import sys, os

from ui_manager import UIManager
from exponential_spin_box import ExponentialSpinBox
from parameter_dictionary import ParameterDictionary
from parameter_table import ParameterTable

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    # Create an instance of ParameterDictionary
    parameter_dictionary = ParameterDictionary()
    parameter_dictionary['a'] = 1.11E+01
    parameter_dictionary['b'] = 2.22E+02
    parameter_dictionary['c'] = 3.33E+03

    # Create an instance of ParameterTable
    ex = ParameterTable(parameter_dictionary)
    ex.display()

    ui_manager = UIManager()
    ui_manager.apply_theme(ex)
    ex.show()
    sys.exit(app.exec())
