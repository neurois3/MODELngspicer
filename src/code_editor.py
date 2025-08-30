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
import re

from code_view import CodeView

class CodeEditor(CodeView):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__tab_style = 'Soft' # or 'Hard'
        self.__tab_spacing = 4


    def tabStyle(self):
        return self.__tab_style


    def setTabStyle(self, style:str):
        if style not in ['Soft', 'Hard']:
            raise ValueError(f"Invalid tab style: {style}. Must be 'Soft' or 'Hard'.")
        self.__tab_style = style


    def tabSpacing(self):
        return self.__tab_spacing


    def setTabSpacing(self, spacing:int):
        if not isinstance(spacing, int):
            raise TypeError(f"spacing must be an integer, got {type(spacing).__name__}")
        if spacing < 1:
            raise ValueError(f"spacing must be a positive integer, got {spacing}")
        self.__tab_spacing = spacing

        # Apply the specified tab spacing to the document
        doc = self.document()
        opt = QtGui.QTextOption(doc.defaultTextOption())
        opt.setTabStopDistance(self.fontMetrics().horizontalAdvance(' ') * spacing)
        doc.setDefaultTextOption(opt)


    @override
    def keyPressEvent(self, event):
        mod = event.modifiers()
        key = event.key()
        if key == Qt.Key_Return:
            self.handleReturn()
        elif key == Qt.Key_Tab:
            self.handleTab()
        elif key == Qt.Key_Backspace:
            self.handleBackspace()
        else:
            super().keyPressEvent(event)


    def handleReturn(self):
        cursor = self.textCursor()

        # Auto indentation
        indent = re.match(r'^\s*', cursor.block().text()).group()
        self.insertPlainText('\n' + indent)


    def handleTab(self):
        if self.__tab_style == 'Hard':
            # Hard tab
            self.insertPlainText('\t')
        else:
            # Soft tab
            cursor = self.textCursor()
            prev_text = cursor.block().text()[0:cursor.positionInBlock()]
            prev_text_length = len(prev_text.replace('\t', ' ' * self.__tab_spacing))

            insert_count = self.__tab_spacing - prev_text_length % self.__tab_spacing
            self.insertPlainText(' ' * insert_count)


    def handleBackspace(self):
        cursor = self.textCursor()
        prev_text = cursor.block().text()[0:cursor.positionInBlock()]
        prev_text_length = len(prev_text.replace('\t', ' ' * self.__tab_spacing))

        if (not cursor.hasSelection()) and prev_text.isspace() and prev_text.endswith(' '):
            delete_count = (prev_text_length + self.__tab_spacing - 1) % self.__tab_spacing + 1
        else:
            delete_count = 1

        for i in range(delete_count):
            cursor.deletePreviousChar()


    def open_(self, file_name):
        if not file_name:
            return
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                self.setPlainText(f.read())
                self.document().setModified(False)

        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'Open Error', f"Failed to open file:\n{e}")


    def save_(self, file_name):
        if not file_name:
            return
        try:
            with open(file_name, 'w', encoding='utf-8') as f:
                f.write(self.toPlainText())
                self.document().setModified(False)

        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'Save Error', f"Failed to save file:\n{e}")
