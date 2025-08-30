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

from graph import Graph
from ui_manager import UIManager
from parameter_io import ParameterIO
from code_editor_window import CodeEditorWindow
import ngspice_con


class LineEdit(QtWidgets.QLineEdit):
    """A custom QLineEdit that emits a signal upon double-clicking."""

    # Signal emitted when double-clicked
    doubleClicked = Signal()

    @override
    def mouseDoubleClickEvent(self, event):
        self.doubleClicked.emit()


class SimulationPanel(QtWidgets.QMainWindow):


    def __init__(self, param_dict, default_title, parent=None):
        super().__init__(parent)

        self.__param_dict = param_dict
        self.__default_title = default_title
        self.__script_file = ''
        self.__data_file = ''
        self.__enabled = True

        # Set the default window title
        self.setWindowTitle(default_title)

        # Setup the central Graph widget
        self.__graph = Graph()
        self.__graph.initialize()
        self.setCentralWidget(self.__graph)

        ui_manager = UIManager()
        ui_manager.themeChanged.connect(self.update_)

        # Setup the menu bar
        SIMULATION_menu = self.menuBar().addMenu('&Simulation')
        GRAPH_menu = self.menuBar().addMenu('&Graph')

        # "Simulation">"Select Ngspice Script..."
        action = QtGui.QAction('Select Ngspice Script...', self)
        action.triggered.connect(self.browseScriptFile)
        SIMULATION_menu.addAction(action)

        # "Simulation">"Select Data..."
        action = QtGui.QAction('Select Data...', self)
        action.triggered.connect(self.browseDataFile)
        SIMULATION_menu.addAction(action)

        SIMULATION_menu.addSeparator()

        # "Simulation">"Enable/Disable Simulation"
        action = QtGui.QAction('Enable/Disable Simulation', self)
        action.triggered.connect(self.toggleEnabled)
        SIMULATION_menu.addAction(action)

        # "Simulation">"Rename Title"
        action = QtGui.QAction('Rename Title', self)
        action.triggered.connect(self.renameTitle)
        SIMULATION_menu.addAction(action)

        # "Simulation">"Reset"
        action = QtGui.QAction('Reset', self)
        action.triggered.connect(self.reset)
        SIMULATION_menu.addAction(action)

        # "Graph">"Axis Titles"
        action = QtGui.QAction('Axis Titles', self)
        action.triggered.connect(self.setAxisTitles)
        GRAPH_menu.addAction(action)

        # "Graph">"Log Scale"
        log_scale_menu = GRAPH_menu.addMenu('Log Scale')

        # "Graph">"Log Scale">"X"
        self.__LOGSCALE_X_action = QtGui.QAction('X', self)
        self.__LOGSCALE_X_action.triggered.connect(self.toggleLogScaleX)
        self.__LOGSCALE_X_action.setCheckable(True)
        self.__LOGSCALE_X_action.setChecked(self.__graph.logScaleX())
        log_scale_menu.addAction(self.__LOGSCALE_X_action)

        # "Graph">"Log Scale">"Y"
        self.__LOGSCALE_Y_action = QtGui.QAction('Y', self)
        self.__LOGSCALE_Y_action.triggered.connect(self.toggleLogScaleY)
        self.__LOGSCALE_Y_action.setCheckable(True)
        self.__LOGSCALE_Y_action.setChecked(self.__graph.logScaleY())
        log_scale_menu.addAction(self.__LOGSCALE_Y_action)

        # "Graph">"Coordinates"
        coordinates_menu = GRAPH_menu.addMenu('Coordinates')
        self.__COORDINATES_actions = {}
        
        # "Graph">"Coordinates">"Cartesian"
        self.__COORDINATES_actions['Cartesian'] = QtGui.QAction('Cartesian', self)
        self.__COORDINATES_actions['Cartesian'].triggered.connect(self.setCartesianCoordinates)

        # "Graph">"Coordinates">"Polar"
        self.__COORDINATES_actions['Polar'] = QtGui.QAction('Polar', self)
        self.__COORDINATES_actions['Polar'].triggered.connect(self.setPolarCoordinates)

        # "Graph">"Coordinates">"Smith Chart"
        self.__COORDINATES_actions['Smith Chart'] = QtGui.QAction('Smith Chart', self)
        self.__COORDINATES_actions['Smith Chart'].triggered.connect(self.setSmithCoordinates)

        for key, action in self.__COORDINATES_actions.items():
            action.setCheckable(True)
            action.setChecked(key == 'Cartesian')
            coordinates_menu.addAction(action)

        # Setup the status bar
        status_bar = self.statusBar()
        status_bar.setStyleSheet('QStatusBar::item { border: None; }')

        # Status bar >"Enable Simulation"
        self.__enabled_checkbox = QtWidgets.QCheckBox('Enable Simulation')
        self.__enabled_checkbox.setToolTip('Disabling simulation helps reduce runtime when not needed')
        self.__enabled_checkbox.setChecked(self.__enabled)
        self.__enabled_checkbox.checkStateChanged.connect(self.checkboxStateChanged)

        status_bar.addWidget(self.__enabled_checkbox)

        # Status bar >"Script:"
        self.__script_edit = LineEdit()
        self.__script_edit.setToolTip('Double-click to open with an editor')
        self.__script_edit.setReadOnly(True)
        self.__script_edit.doubleClicked.connect(self.openScriptInEditor)

        status_bar.addPermanentWidget(QtWidgets.QLabel('Script:'))
        status_bar.addPermanentWidget(self.__script_edit)

        # Status bar >"Data:"
        self.__data_edit = LineEdit()
        self.__data_edit.setToolTip('Double-click to open with an editor')
        self.__data_edit.setReadOnly(True)
        self.__data_edit.doubleClicked.connect(self.openDataInEditor)

        status_bar.addPermanentWidget(QtWidgets.QLabel('Data:'))
        status_bar.addPermanentWidget(self.__data_edit)


    def enabled(self):
        return self.__enabled


    def setEnabled(self, value):
        if not isinstance(value, bool):
            raise ValueError("setEnabled(): `value` must be a boolean.")
        self.__enabled = value
        self.__enabled_checkbox.setChecked(value)

    
    def scriptFile(self):
        return self.__script_file


    def setScriptFile(self, value):
        if not isinstance(value, str):
            raise ValueError("setScriptFile(): `value` must be a string.")
        self.__script_file = value
        self.__script_edit.setText(value)


    def dataFile(self):
        return self.__data_file


    def setDataFile(self, value):
        if not isinstance(value, str):
            raise ValueError("setDataFile(): `value` must be a string.")
        self.__data_file = value
        self.__data_edit.setText(value)


    def graph(self):
        return self.__graph


    @Slot()
    def browseScriptFile(self):
        file_name, type_ = QtWidgets.QFileDialog.getOpenFileName(self,\
                'Open...', '', 'SPICE Script (*.sp *.cir *.spice);;All Files (*)')
        if not file_name:
            return
        self.setScriptFile(file_name)
        self.update_()


    @Slot()
    def browseDataFile(self):
        file_name, type_ = QtWidgets.QFileDialog.getOpenFileName(self,\
                'Open...', '', 'Text Files (*.txt);;All Files (*)')
        if not file_name:
            return
        self.setDataFile(file_name)
        self.update_()

    
    @Slot()
    def toggleEnabled(self):
        self.setEnabled(not self.enabled())
        self.update_()


    @Slot()
    def renameTitle(self):
        text, ok = QtWidgets.QInputDialog.getText(self,\
                'Rename Title', 'Title:', QtWidgets.QLineEdit.Normal, self.windowTitle())
        if ok and text:
            self.setWindowTitle(text)


    @Slot()
    def reset(self):
        self.setScriptFile('')
        self.setDataFile('')
        self.setEnabled(True)

        # Reset the window title
        self.setWindowTitle(self.__default_title)

        # Reset the graph
        self.__graph.setCoordinates('Cartesian')
        self.__graph.setLogScaleX(False)
        self.__graph.setLogScaleY(False)

        self.update_()

        self.__graph.setLabel(text=None, units=None, axis='bottom')
        self.__graph.setLabel(text=None, units=None, axis='left')
        self.__graph.setRange(xRange=(0, 1), yRange=(0, 1), padding=0)
        self.__graph.enableAutoRange(x=True, y=True)


    @Slot()
    def toggleLogScaleX(self):
        self.__graph.setLogScaleX(not self.__graph.logScaleX())
        self.update_()


    @Slot()
    def toggleLogScaleY(self):
        self.__graph.setLogScaleY(not self.__graph.logScaleY())
        self.update_()


    @Slot()
    def setCartesianCoordinates(self):
        self.__graph.setCoordinates('Cartesian')
        self.update_()


    @Slot()
    def setPolarCoordinates(self):
        self.__graph.setCoordinates('Polar')
        d, ok = QtWidgets.QInputDialog.getDouble(self,\
                'Polar Coordinates', 'Radius:', 1.0, 0.0, 1000.0, 2,\
                Qt.WindowFlags(), 0.1)
        if ok:
            self.__graph.setPolarRadius(d)
        self.update_()


    @Slot()
    def setSmithCoordinates(self):
        self.__graph.setCoordinates('Smith Chart')
        self.update_()


    @Slot()
    def setAxisTitles(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle('Set Axis Titles')

        # X Axis
        Xtitle_edit = QtWidgets.QLineEdit()
        Xunit_combo = QtWidgets.QComboBox()
        Xunit_combo.setEditable(True)
        Xunit_combo.addItems(['', 'V', 'A', 'Ω', 's', 'Hz'])

        # Y axis
        Ytitle_edit = QtWidgets.QLineEdit()
        Yunit_combo = QtWidgets.QComboBox()
        Yunit_combo.setEditable(True)
        Yunit_combo.addItems(['', 'V', 'A', 'Ω', 's', 'Hz'])

        # Layout
        layout = QtWidgets.QGridLayout(dialog)
        layout.addWidget(QtWidgets.QLabel('X Axis Title:'), 0, 0)
        layout.addWidget(Xtitle_edit, 0, 1)
        layout.addWidget(QtWidgets.QLabel('Unit:'), 0, 2)
        layout.addWidget(Xunit_combo, 0, 3)
        layout.addWidget(QtWidgets.QLabel('Y Axis Title:'), 1, 0)
        layout.addWidget(Ytitle_edit, 1, 1)
        layout.addWidget(QtWidgets.QLabel('Unit:'), 1, 2)
        layout.addWidget(Yunit_combo, 1, 3)

        # Buttons
        button_box = QtWidgets.QDialogButtonBox(\
                QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,\
                parent=dialog)
        layout.addWidget(button_box, 2, 0, 1, 4)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)

        if dialog.exec() == QtWidgets.QDialog.Accepted:
            self.__graph.setAxisTitleX(Xtitle_edit.text())
            self.__graph.setAxisUnitsX(Xunit_combo.currentText())
            self.__graph.setAxisTitleY(Ytitle_edit.text())
            self.__graph.setAxisUnitsY(Yunit_combo.currentText())
            self.update_()


    @Slot()
    def checkboxStateChanged(self):
        self.setEnabled(self.__enabled_checkbox.isChecked())
        self.update_()


    @Slot()
    def openScriptInEditor(self):
        editor = CodeEditorWindow()
        if self.__script_file:
            editor.open_(self.__script_file)
        editor.show()


    @Slot()
    def openDataInEditor(self):
        editor = CodeEditorWindow()
        if self.__data_file:
            editor.open_(self.__data_file)
        editor.show()


    @Slot()
    def update_(self):
        # Update check states of the menu actions
        self.__LOGSCALE_X_action.setChecked(self.__graph.logScaleX())
        self.__LOGSCALE_Y_action.setChecked(self.__graph.logScaleY())
        for key, action in self.__COORDINATES_actions.items():
            action.setChecked(key == self.__graph.coordinates())

        if not self.__enabled:
            return

        # Initialize graph view
        self.__graph.initialize()

        try:
            # Run ngspice simulation and plot the result
            if self.__script_file:
                # Write parameters to "model.txt"
                working_dir = os.path.dirname(os.path.abspath(self.__script_file))
                output_file = os.path.join(working_dir, 'model.txt')
                parameter_io = ParameterIO()
                parameter_io.write(self.__param_dict, output_file)

                # Run ngspice_con
                ngspice_con.run(self.__script_file)

                # Plot the simulation result
                root, ext = os.path.splitext(self.__script_file)
                result_file = root + '.txt'

                ui_manager = UIManager()
                symbol_color = 'k' if ui_manager.theme() == 'Light' else 'w'
                self.__graph.plotFile(\
                        result_file,\
                        symbol_pen=symbol_color,\
                        symbol_brush=symbol_color)

            # Plot the reference data
            if self.__data_file:
                self.__graph.plotFile(self.__data_file,\
                        symbol_pen='r',\
                        symbol_brush='r')

        except Exception as e:
            print(str(e))
