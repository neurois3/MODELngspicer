from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
from typing import override

class ExponentialSpinBox(QtWidgets.QAbstractSpinBox):

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
