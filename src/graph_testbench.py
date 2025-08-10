from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
import sys, os

from graph import Graph
from ui_manager import UIManager

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex  = Graph()
    ex.initialize('Smith Chart')

    ui_manager = UIManager()
    ui_manager.apply_theme(ex)
    ex.show()
    sys.exit(app.exec())

