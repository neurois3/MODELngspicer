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


    @property
    def tab_style(self):
        return self.__tab_style


    @tab_style.setter
    def tab_style(self, style:str):
        if style not in ['Soft', 'Hard']:
            raise ValueError(f"Invalid tab style: {style}. Must be 'Soft' or 'Hard'.")
        self.__tab_style = style


    @property
    def tab_spacing(self):
        return self.__tab_spacing


    @tab_spacing.setter
    def tab_spacing(self, spacing:int):
        if not isinstance(spacing, int):
            raise TypeError(f'tab_spacing must be an integer, got {type(spacing).__name__}')
        if spacing < 1:
            raise ValueError(f'tab_spacing must be a positive integer, got {spacing}')
        self.__tab_spacing = spacing

        opt = QtGui.QTextOption(self.document().defaultTextOption())
        opt.setTabStopDistance(self.fontMetrics().horizontalAdvance(' ') * spacing)
        self.document().setDefaultTextOption(opt)


    @override
    def keyPressEvent(self, event):
        mod = event.modifiers()
        key = event.key()

        if key == Qt.Key_Return:
            self.handle_return()
        elif key == Qt.Key_Tab:
            self.handle_tab()
        elif key == Qt.Key_Backspace:
            self.handle_backspace()
        else:
            super().keyPressEvent(event)


    def handle_return(self):
        cursor = self.textCursor()
        block_text = cursor.block().text()

        indent = re.match(r'^\s*', block_text).group()
        self.insertPlainText('\n' + indent)


    def handle_tab(self):
        if self.tab_style == 'Hard':
            self.insertPlainText('\t')
        else:
            cursor = self.textCursor()
            prev_text = cursor.block().text()[0:cursor.positionInBlock()]
            prev_text_length = len(prev_text.replace('\t', ' ' * self.tab_spacing))

            insert_count = self.tab_spacing - prev_text_length % self.tab_spacing
            self.insertPlainText(' ' * insert_count)


    def handle_backspace(self):
        cursor = self.textCursor()
        prev_text = cursor.block().text()[0:cursor.positionInBlock()]
        prev_text_length = len(prev_text.replace('\t', ' ' * self.tab_spacing))

        if (not cursor.hasSelection()) and prev_text.isspace() and prev_text.endswith(' '):
            delete_count = (prev_text_length + self.tab_spacing - 1) % self.tab_spacing + 1
        else:
            delete_count = 1

        for i in range(delete_count):
            cursor.deletePreviousChar()


    def open_file(self, filename):
        if not filename:
            return

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.setPlainText(f.read())
                self.document().setModified(False)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'Open Error', f'Failed to open file:\n{e}')


    def save_file(self, filename):
        if not filename:
            return

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.toPlainText())
                self.document().setModified(False)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'Save Error', f'Failed to save file:\n{e}')
