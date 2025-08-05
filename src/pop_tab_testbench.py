from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
import sys, os

from pop_tab import PopTab
from ui_theme import apply_theme

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    # Create an instance of PopTab with tab pages
    ex = PopTab()
    ex.addTab(QtWidgets.QFrame(), 'Tab 1')
    ex.addTab(QtWidgets.QFrame(), 'Tab 2')
    ex.addTab(QtWidgets.QFrame(), 'Tab 3')
    ex.addTab(QtWidgets.QFrame(), 'Tab 4')
    ex.addTab(QtWidgets.QFrame(), 'Tab 5')

    apply_theme(ex)
    ex.show()
    sys.exit(app.exec())
