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
import sys, os

from code_editor import CodeEditor
from ui_manager import UIManager
from syntax_highlighter import *

class CodeEditorWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__filename = ''
        self.code_editor = CodeEditor()
        self.code_editor.modificationChanged.connect(self.update_window_title)
        self.setCentralWidget(self.code_editor)

        self.ui_manager = UIManager()
        self.ui_manager.apply_theme(self)
        self.ui_manager.themeChanged.connect(lambda: self.ui_manager.apply_theme(self))

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')
        options_menu = menu_bar.addMenu('&Options')

        # "File">"Open..."
        action = QtGui.QAction('&Open...', self)
        action.setShortcut('Ctrl+O')
        action.triggered.connect(self.open)
        file_menu.addAction(action)

        # "File">"Save..."
        action = QtGui.QAction('&Save...', self)
        action.setShortcut('Ctrl+S')
        action.triggered.connect(self.save)
        file_menu.addAction(action)

        # "File">"Save as..."
        action = QtGui.QAction('&Save as...', self)
        action.setShortcut('Ctrl+Shift+S')
        action.triggered.connect(self.save_as)
        file_menu.addAction(action)

        # "Options">"Tab Style"
        tab_style_menu = options_menu.addMenu('Tab Style')

        # "Options">"Tab Style">"Soft Tabs", "Hard Tabs"
        self.soft_tabs_action = QtGui.QAction('Soft Tabs', self)
        self.soft_tabs_action.triggered.connect(self.set_soft_tab)
        self.soft_tabs_action.setCheckable(True)
        self.soft_tabs_action.setChecked(self.code_editor.tab_style == 'Soft')
        tab_style_menu.addAction(self.soft_tabs_action)

        # "Options">"Tab Style">"Hard Tabs"
        self.hard_tabs_action = QtGui.QAction('Hard Tabs', self)
        self.hard_tabs_action.triggered.connect(self.set_hard_tab)
        self.hard_tabs_action.setCheckable(True)
        self.hard_tabs_action.setChecked(self.code_editor.tab_style == 'Hard')
        tab_style_menu.addAction(self.hard_tabs_action)

        # "Options">"Tab Spacing"
        action = QtGui.QAction('Tab Spacing', self)
        action.triggered.connect(self.set_tab_spacing)
        options_menu.addAction(action)

        options_menu.addSeparator()

        # "Options">"Language"
        language_menu = options_menu.addMenu('Language')

        # "Options">"Language">"Plain Text", "C/C++", "Matlab/Octave", "Python", "SPICE"
        self.language_actions = []
        for language in ['Plain Text', 'C/C++', 'Matlab/Octave', 'Python', 'SPICE']:
            action = QtGui.QAction(language, self)
            action.setCheckable(True)
            action.setChecked(language == 'Plain Text')
            action.triggered.connect(\
                    lambda checked, language=language:\
                    self.set_language(language))

            self.language_actions.append(action)
            language_menu.addAction(action)

        
        # Update the window title and resize the window
        self.update_window_title()
        self.resize(600, 400)


    @property
    def filename(self):
        return self.__filename


    @filename.setter
    def filename(self, filename):
        self.__filename = filename
        self.update_window_title()


    @Slot()
    def update_window_title(self):
        title = os.path.basename(self.filename) if self.filename else 'New'
        doc = self.code_editor.document()
        if doc.isModified():
            title = '*' + title

        self.setWindowTitle(title)


    def open_file(self, filename):
        if not filename:
            return
        self.code_editor.open_file(filename)
        self.filename = filename

        root, ext = os.path.splitext(filename)
        ext = ext.lower()
        self.set_language(\
                     'C/C++'            if ext in ['.c'  , '.h'  , '.cpp', '.hpp']\
                else 'Matlab/Octave'    if ext in ['.m']\
                else 'Python'           if ext in ['.py' , '.pyw', '.pyc', '.pyd']\
                else 'SPICE'            if ext in ['.spice', '.sp', '.cir', '.mod']\
                else 'Plain Text')


    @Slot()
    def open(self):
        doc = self.code_editor.document()
        if doc.isModified():
            message_box = QtWidgets.QMessageBox(self)
            message_box.setText('Discard changes?')
            message_box.setStandardButtons(QtWidgets.QMessageBox.Ok\
                    | QtWidgets.QMessageBox.Cancel)
            answer = message_box.exec()
            if answer == QtWidgets.QMessageBox.Cancel:
                return

        filename, type_ = QtWidgets.QFileDialog.getOpenFileName(self,\
                'Open File', '', 'All Files (*)')
        if filename:
            self.open_file(filename)


    @Slot()
    def save(self):
        if not self.filename:
            self.save_as()
            return

        self.code_editor.save_file(self.filename)
        self.code_editor.document().setModified(False)


    @Slot()
    def save_as(self):
        parent_dir = os.path.dirname(self.filename)
        if self.filename and os.path.isdir(parent_dir):
            dir_ = parent_dir
        else:
            dir_ = ''

        filename, type_ = QtWidgets.QFileDialog.getSaveFileName(self,\
                'Save File', dir_, 'All Files (*)')
        if not filename:
            return
        self.code_editor.save_file(filename)
        self.code_editor.document().setModified(False)
        self.filename = filename


    @Slot()
    def set_soft_tab(self):
        self.code_editor.tab_style = 'Soft'
        self.soft_tabs_action.setChecked(True)
        self.hard_tabs_action.setChecked(False)


    @Slot()
    def set_hard_tab(self):
        self.code_editor.tab_style = 'Hard'
        self.soft_tabs_action.setChecked(False)
        self.hard_tabs_action.setChecked(True)


    @Slot()
    def set_tab_spacing(self):
        i, ok = QtWidgets.QInputDialog.getInt(self, 'Tab Spacing', 'Tab Spacing:',\
                self.code_editor.tab_spacing, 2, 16, 1)
        if ok:
            self.code_editor.tab_spacing = i


    @Slot()
    def set_language(self, language):
        syntax_highlighter = {\
                'Plain Text'    : SyntaxHighlighter,\
                'C/C++'         : SyntaxHighlighter,\
                'Matlab/Octave' : SyntaxHighlighter_Matlab_Octave,\
                'Python'        : SyntaxHighlighter_Python,\
                'SPICE'         : SyntaxHighlighter_SPICE,\
                }
        if language not in syntax_highlighter:
            raise ValueError(f'Unknown language: {language}')

        editor = self.code_editor
        editor.syntax_highlighter = syntax_highlighter[language](editor.document())

        for action in self.language_actions:
            action.setChecked(action.text() == language)
