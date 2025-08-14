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
from typing import override


class ExponentialSpinBox(QtWidgets.QAbstractSpinBox):
    """A custom spinbox widget for handling values in exponential notation,
    with steps for exponential adjustment."""

    # Signal emitted when the value is updated
    valueChanged = Signal(float)


    def __init__(self, parent=None):
        super().__init__(parent)
        # Initialize the spinbox with a default value
        self.setValue(0.0)
        # Connect the editingFinished signal to a custom slot
        self.editingFinished.connect(self.finishEditing)


    @Slot()
    def finishEditing(self):
        # Convert the user's input string into a numerical value,
        # then reformat it back into exponential notation.
        value = self.value()
        self.setValue(value)


    def value(self) -> float:
        # Retrieve the current value from the line edit
        result = 0.0
        lineEdit = self.lineEdit()
        try:
            result = float(lineEdit.text())
        except ValueError:
            pass
        return result


    def setValue(self, value):
        # Set the value in exponential format and emit valueChanged signal
        lineEdit = self.lineEdit()
        lineEdit.setText('{:.3E}'.format(value))
        self.valueChanged.emit(self.value())


    @override
    def stepEnabled(self):
        # Allow both step-up and step-down functionality
        return (QtWidgets.QAbstractSpinBox.StepUpEnabled\
                | QtWidgets.QAbstractSpinBox.StepDownEnabled)


    @override
    def stepBy(self, steps):
        # Adjust the current value by multiplying with a small exponential factor
        a = self.value()
        b = a * (1.01**steps) if a != 0\
                else (-1E-15) if steps < 0\
                else (+1E-15)

        self.setValue(b)


    @override
    def validate(self, input, pos):
        # Validate the input as a double-precision floating point number
        validator = QtGui.QDoubleValidator()
        return validator.validate(input, pos)
