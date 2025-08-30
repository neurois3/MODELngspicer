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
        self.__file_name = ''
        self.__code_editor = CodeEditor()
        self.__code_editor.modificationChanged.connect(self.updateWindowTitle)
        self.setCentralWidget(self.__code_editor)

        ui_manager = UIManager()
        ui_manager.applyTheme(self)
        ui_manager.themeChanged.connect(lambda: ui_manager.applyTheme(self))

        FILE_menu = self.menuBar().addMenu('&File')
        OPTIONS_menu = self.menuBar().addMenu('&Options')

        # "File">"Open..."
        action = QtGui.QAction('&Open...', self)
        action.setShortcut('Ctrl+O')
        action.triggered.connect(self.openEvent)
        FILE_menu.addAction(action)

        # "File">"Save..."
        action = QtGui.QAction('&Save...', self)
        action.setShortcut('Ctrl+S')
        action.triggered.connect(self.saveEvent)
        FILE_menu.addAction(action)

        # "File">"Save as..."
        action = QtGui.QAction('&Save as...', self)
        action.setShortcut('Ctrl+Shift+S')
        action.triggered.connect(self.saveAsEvent)
        FILE_menu.addAction(action)

        # "Options">"Tab Style"
        TAB_STYLE_menu = OPTIONS_menu.addMenu('Tab Style')

        # "Options">"Tab Style">"Soft Tabs", "Hard Tabs"
        self.__SOFT_TABS_action = QtGui.QAction('Soft Tabs', self)
        self.__SOFT_TABS_action.triggered.connect(self.setSoftTab)
        self.__SOFT_TABS_action.setCheckable(True)
        self.__SOFT_TABS_action.setChecked(self.__code_editor.tabStyle() == 'Soft')
        TAB_STYLE_menu.addAction(self.__SOFT_TABS_action)

        # "Options">"Tab Style">"Hard Tabs"
        self.__HARD_TABS_action = QtGui.QAction('Hard Tabs', self)
        self.__HARD_TABS_action.triggered.connect(self.setHardTab)
        self.__HARD_TABS_action.setCheckable(True)
        self.__HARD_TABS_action.setChecked(self.__code_editor.tabStyle() == 'Hard')
        TAB_STYLE_menu.addAction(self.__HARD_TABS_action)

        # "Options">"Tab Spacing"
        action = QtGui.QAction('Tab Spacing', self)
        action.triggered.connect(self.setTabSpacing)
        OPTIONS_menu.addAction(action)

        OPTIONS_menu.addSeparator()

        # "Options">"Language"
        LANGUAGE_menu = OPTIONS_menu.addMenu('Language')

        # "Options">"Language">"Plain Text", "Python", "SPICE"
        self.__LANGUAGE_actions = []
        for language in ['Plain Text', 'Python', 'SPICE']:
            action = QtGui.QAction(language, self)
            action.setCheckable(True)
            action.setChecked(language == 'Plain Text')
            action.triggered.connect(\
                    lambda checked, language=language:\
                    self.setLanguage(language))

            self.__LANGUAGE_actions.append(action)
            LANGUAGE_menu.addAction(action)

        
        # Update the window title and resize the window
        self.updateWindowTitle()
        self.resize(600, 400)


    def fileName(self):
        return self.__file_name


    def setFileName(self, file_name):
        self.__file_name = file_name
        self.updateWindowTitle()


    @Slot()
    def updateWindowTitle(self):
        title = os.path.basename(self.__file_name) if self.__file_name else 'New'
        doc = self.__code_editor.document()
        if doc.isModified():
            title = '*' + title

        self.setWindowTitle(title)


    def open_(self, file_name):
        if not file_name:
            return
        self.__code_editor.open_(file_name)
        self.__file_name = file_name
        self.updateWindowTitle()

        root, ext = os.path.splitext(file_name)
        ext = ext.lower()
        self.setLanguage(\
                     'Python' if ext in ['.py', '.pyw', '.pyc', '.pyd']\
                else 'SPICE'  if ext in ['.cir', '.sp', '.spice', '.mod']\
                else 'Plain Text')


    @Slot()
    def openEvent(self):
        doc = self.__code_editor.document()
        if doc.isModified():
            message_box = QtWidgets.QMessageBox(self)
            message_box.setText('Discard changes?')
            message_box.setStandardButtons(QtWidgets.QMessageBox.Ok\
                    | QtWidgets.QMessageBox.Cancel)
            answer = message_box.exec()
            if answer == QtWidgets.QMessageBox.Cancel:
                return

        file_name, type_ = QtWidgets.QFileDialog.getOpenFileName(self,\
                'Open File', '', 'All Files (*)')
        if file_name:
            self.open_(file_name)


    @Slot()
    def saveEvent(self):
        if not self.__file_name:
            self.saveAsEvent()
            return

        self.__code_editor.save_(self.__file_name)
        self.__code_editor.document().setModified(False)


    @Slot()
    def saveAsEvent(self):
        parent_dir = os.path.dirname(self.__file_name)
        if self.__file_name and os.path.isdir(parent_dir):
            dir_ = parent_dir
        else:
            dir_ = ''

        file_name, type_ = QtWidgets.QFileDialog.getSaveFileName(self,\
                'Save File', dir_, 'All Files (*)')
        if file_name:
            self.__code_editor.save_(file_name)
            self.__code_editor.document().setModified(False)
            self.__file_name = file_name


    @Slot()
    def setSoftTab(self):
        self.__code_editor.setTabStyle('Soft')
        self.__SOFT_TABS_action.setChecked(True)
        self.__HARD_TABS_action.setChecked(False)


    @Slot()
    def setHardTab(self):
        self.__code_editor.setTabStyle('Hard')
        self.__SOFT_TABS_action.setChecked(False)
        self.__HARD_TABS_action.setChecked(True)


    @Slot()
    def setTabSpacing(self):
        i, ok = QtWidgets.QInputDialog.getInt(self, 'Tab Spacing', 'Tab Spacing:',\
                self.__code_editor.tabSpacing(), 2, 16, 1)
        if ok:
            self.__code_editor.setTabSpacing(i)


    @Slot()
    def setLanguage(self, language:str):
        syntax_highlighter = {\
                'Plain Text'    : SyntaxHighlighter,\
                'Python'        : SyntaxHighlighter_Python,\
                'SPICE'         : SyntaxHighlighter_SPICE,\
                }
        if language not in syntax_highlighter:
            raise ValueError(f"Unknown language: {language}")

        doc = self.__code_editor.document()
        self.__code_editor.setSyntaxHighlighter(syntax_highlighter[language](doc))

        for action in self.__LANGUAGE_actions:
            action.setChecked(action.text() == language)


    @override
    def closeEvent(self, event: QtGui.QCloseEvent):
        doc = self.__code_editor.document()
        if doc.isModified():
            reply = QtWidgets.QMessageBox.question(\
                    self, "Unsaved Changes",\
                    "The document has unsaved changes. Do you want to save before closing?",\
                    QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Discard | QtWidgets.QMessageBox.Cancel,\
                    QtWidgets.QMessageBox.Save)
            if reply == QtWidgets.QMessageBox.Save:
                self.saveEvent()
            elif reply == QtWidgets.QMessageBox.Cancel:
                event.ignore()
                return

        event.accept()
