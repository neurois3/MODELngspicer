from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
import sys, os

from exponential_spin_box import ExponentialSpinBox
from parameter_items import ParameterItems

class ParameterTable(QtWidgets.QTableWidget):
    """ A custom table widget for displaying and managing model parameters.

    Attributes:
        valueChanged (Signal): Signal emitted whenever parameter values are updated.
        m_items (ParameterItems): Holds the model parameters to be displayed and modified.
    """

    valueChanged = Signal()
    m_items : ParameterItems

    def __init__(self, items, parent=None):
        """ Initializes the table with given parameters and sets up its layout.

        Args:
            items (ParameterItems): The model parameter items to be used.
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.m_items = items
        self.setupView()

    def setupView(self):
        """ Configures the layout and appearance of the table. """

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
        """ Updates the table with parameter names and values. """

        self.setupView()
        self.setRowCount(self.m_items.count())

        names = self.m_items.name_list()
        for i, name in enumerate(names):
            # Column 1: Parameter name (read-only)
            item = QtWidgets.QTableWidgetItem(name)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.setItem(i, 0, item)

            # Column 2: Parameter value (editable with ExponentialSpinBox)
            spinbox = ExponentialSpinBox()
            spinbox.setValue(self.m_items.value(name))
            spinbox.valueChanged.connect(self.valueChangedEvent)
            self.setCellWidget(i, 1, spinbox)

        # Emit valueChanged signal after setting up the table
        self.valueChanged.emit()

    @Slot()
    def valueChangedEvent(self):
        """ Slot that updates the parameter values based on user input """

        for i in range(self.rowCount()):
            # Retrieve parameter name and updated value
            name = self.item(i, 0).text()
            value = self.cellWidget(i, 1).value()

            # Update the model parameters with the new value
            self.m_items.set_value(name, value)

        # Emit signal to notify that values have changed
        self.valueChanged.emit()
