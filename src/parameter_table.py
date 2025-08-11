from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
import sys, os

from exponential_spin_box import ExponentialSpinBox
from parameter_dictionary import ParameterDictionary

class ParameterTable(QtWidgets.QTableWidget):

    valueChanged = Signal()
    m_parameter_dictionary : ParameterDictionary


    def __init__(self, parameter_dictionary, parent=None):
        super().__init__(parent)
        self.m_parameter_dictionary = parameter_dictionary
        self.setup_layout()


    def setup_layout(self):
        # Clear existing contents from the table
        self.clear()
        
        # Set header dimensions
        self.verticalHeader().setMinimumSectionSize(18)
        self.verticalHeader().setDefaultSectionSize(18)
        self.horizontalHeader().setFixedHeight(18)

        # Set column labels and count
        self.setHorizontalHeaderLabels(['name', 'value'])
        self.setColumnCount(2)


    def display(self):
        self.setup_layout()
        self.setRowCount(len(self.m_parameter_dictionary))

        row = 0
        for key, value in self.m_parameter_dictionary.items():
            # Column 1: parameter name (read-only)
            widget_item = QtWidgets.QTableWidgetItem(key)
            widget_item.setFlags(widget_item.flags() & ~Qt.ItemIsEditable)
            self.setItem(row, 0, widget_item)

            # Column 2: parameter value (editable with ExponentialSpinBox)
            spin_box = ExponentialSpinBox()
            spin_box.setValue(value)
            spin_box.valueChanged.connect(self.spin_box_value_changed)
            self.setCellWidget(row, 1, spin_box)

            # Increment the row index
            row = row + 1

        # Emit the valueChanged signal
        self.valueChanged.emit()


    @Slot()
    def spin_box_value_changed(self):
        for row in range(self.rowCount()):
            # Retrieve parameter name and value
            key = self.item(row, 0).text()
            value = self.cellWidget(row, 1).value()

            # Update parameter dictionary with a new value
            self.m_parameter_dictionary[key] = value

        # Emit the valueChanged signal
        self.valueChanged.emit()
