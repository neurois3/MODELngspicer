# Copyright (C) 2025 ペE(neurois3)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
import sys, os

from exponential_spin_box import ExponentialSpinBox

class ParameterTable(QtWidgets.QTableWidget):

    # Signal emitted when a parameter is updated by the user
    valueChanged = Signal()


    def __init__(self, param_dict:dict, parent=None):
        super().__init__(parent)
        self.__param_dict = param_dict
        self.setup_layout()


    def setup_layout(self):
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
        self.setRowCount(len(self.__param_dict))

        for row, (key, value) in enumerate(self.__param_dict.items()):
            # Column 1: parameter name (read-only)
            widget_item = QtWidgets.QTableWidgetItem(key)
            widget_item.setFlags(widget_item.flags() & ~Qt.ItemIsEditable)
            self.setItem(row, 0, widget_item)

            # Column 2: parameter value (editable with ExponentialSpinBox)
            spin_box = ExponentialSpinBox()
            spin_box.setValue(value)
            spin_box.valueChanged.connect(self.spin_box_changed)
            self.setCellWidget(row, 1, spin_box)

        self.valueChanged.emit()


    @Slot()
    def spin_box_changed(self):
        sender = self.sender()

        for row in range(self.rowCount()):
            if self.cellWidget(row, 1) is sender:
                # Retrieve parameter name and value
                key = self.item(row, 0).text()
                value = sender.value()
                self.__param_dict[key] = value
                break

        self.valueChanged.emit()
