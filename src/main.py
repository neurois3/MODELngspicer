from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
import sys, os

import platform
from main_window import MainWindow

if __name__ == '__main__':
    operating_system = platform.system()
    app_id = 'ModelNgspicer'

    if operating_system == 'Windows':
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    else:
        pass

    app = QtWidgets.QApplication(sys.argv)
    ex  = MainWindow()
    ex.show()
    sys.exit(app.exec())
