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

from ui_manager import UIManager
from syntax_highlighter import SyntaxHighlighter

def get_monospace_font(size:int=9) -> QtGui.QFont:
    """
    Returns a platform-appropriate monospace QFont with fallback options.
    """
    preferred_fonts = {\
            'Windows': ['Consolas', 'Courier New', 'Lucida Console'],\
            'Darwin' : ['Menlo', 'Monaco', 'Courier'],\
            'Linux'  : ['DejaVu Sans Mono', 'Liberation Mono', 'Courier'],\
            }
    os_name = QtCore.QSysInfo.productType().capitalize()
    fallback_fonts = preferred_fonts.get(os_name, ['Courier'])
    
    available_fonts = QtGui.QFontDatabase().families()
    for name in fallback_fonts:
        if name in available_fonts:
            return QtGui.QFont(name, size)

    return QtGui.QFont(QtGui.QFontDatabase.systemFont(\
            QtGui.QFontDatabase.FixedFont).family(), size)


class LineNumberArea(QtWidgets.QWidget):
    """
    A widget that displays line numbers alongside the CodeView editor.
    Painting is delegated to the parent editor.
    """

    def __init__(self, editor):
        super().__init__(editor)
        self.__editor = editor


    @override
    def sizeHint(self):
        return QtCore.QSize(self.__editor.line_number_area_width(), 0)


    @override
    def paintEvent(self, event):
        self.__editor.line_number_area_paint_event(event)


class CodeView(QtWidgets.QPlainTextEdit):
    """
    A custom code editor widget with line numbers, syntax highlighting,
    and current line highlighting.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__line_number_area = LineNumberArea(self)
        self.__syntax_highlighter = SyntaxHighlighter(self.document())

        # Set font
        self.setFont(get_monospace_font(9))

        # Set stylesheet
        self.update_theme()
        ui_manager = UIManager()
        ui_manager.themeChanged.connect(self.update_theme)

        # Configure text rendering options
        opt = QtGui.QTextOption()

        # Set tab width to 4 spaces
        opt.setTabStopDistance(self.fontMetrics().horizontalAdvance(' ') * 4)

        # Disable word wrapping
        opt.setWrapMode(QtGui.QTextOption.NoWrap)

        # Show whitespaces characters
        opt.setFlags(QtGui.QTextOption.ShowTabsAndSpaces)
        self.document().setDefaultTextOption(opt)

        # Connect editor signals to update slots
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)

        # Initialize layout and highlight
        self.update_line_number_area_width(0)
        self.highlight_current_line()


    @property
    def syntax_highlighter(self):
        """
        Returns the current syntax highlighter instance.
        """
        return self.__syntax_highlighter


    @syntax_highlighter.setter
    def syntax_highlighter(self, highlighter):
        """
        Sets a new syntax highlighter for the document.

        Example:
            editor = CodeView()
            editor.syntax_highlighter = SyntaxHighlighter(editor.document())
        """
        self.__syntax_highlighter.setDocument(None)
        self.__syntax_highlighter = highlighter


    def line_number_area_width(self):
        """
        Calculates the width needed to display line numbers based on the number digits.
        """
        digits = 1
        max_num = max(10, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1

        space = 3 + self.fontMetrics().horizontalAdvance('0') * digits
        return space


    @override
    def resizeEvent(self, event):
        """
        Adjusts the geometry of the line number area when the editor is resized.
        """
        super().resizeEvent(event)

        cr = self.contentsRect()
        rect = QtCore.QRect(\
                cr.left(), cr.top(),\
                self.line_number_area_width(), cr.height())

        self.__line_number_area.setGeometry(rect)
    

    @Slot()
    def line_number_area_paint_event(self, event):
        """
        Paints the line numbers in the line number area.
        """
        # Fill background
        painter = QtGui.QPainter(self.__line_number_area)
        painter.fillRect(event.rect(), self.line_number_background_color)

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        offset = self.contentOffset()
        top = self.blockBoundingGeometry(block).translated(offset).top()
        bottom = top + self.blockBoundingRect(block).height()

        # Iterate through visible blocks and draw line numbers
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(self.line_number_color) # Line number color
                painter.drawText(0, top, self.__line_number_area.width(),\
                        self.fontMetrics().height(), Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

        painter.end()


    @Slot()
    def update_theme(self):
        ui_manager = UIManager()
        if ui_manager.theme == 'Light':
            self.current_line_background_color = QtGui.QColor('#bfbfbf')
            self.line_number_background_color = QtGui.QColor('#eaeaea')
            self.line_number_color = QtGui.QColor('#9fa6a7')
            self.setStyleSheet(\
                    f"""
                    QPlainTextEdit {{
                        font-family     : {self.font().family()};
                        font-size       : {self.font().pointSize()}pt;
                        background-color: #eaeaea;
                        color           : #17172c;
                    }}
                    """)
        else:
            self.current_line_background_color = QtGui.QColor('#404040')
            self.line_number_background_color = QtGui.QColor('#151515')
            self.line_number_color = QtGui.QColor('#605958')
            self.setStyleSheet(\
                    f"""
                    QPlainTextEdit {{
                        font-family     : {self.font().family()};
                        font-size       : {self.font().pointSize()}pt;
                        background-color: #151515;
                        color           : #e8e8d3;
                    }}
                    """)


    @Slot()
    def update_line_number_area_width(self, block_count):
        """
        Updates the left margin of the editor to accommodate the line number area.
        """
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    
    @Slot()
    def update_line_number_area(self, rect, dy):
        """
        Handles scrolling and repainting of the line number area.
        """
        if dy:
            self.__line_number_area.scroll(0, dy)
        else:
            width = self.__line_number_area.width()
            self.__line_number_area.update(0, rect.y(), width, rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)


    @Slot()
    def highlight_current_line(self):
        """
        Highlights the line where the cursor is currenly located.
        """
        extra_selections = []
        if not self.isReadOnly():
            selection = QtWidgets.QTextEdit.ExtraSelection()
            selection.format.setBackground(self.current_line_background_color) # Highlight color
            selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)

        self.setExtraSelections(extra_selections)
