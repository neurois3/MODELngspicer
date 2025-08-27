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
from parameter_io import write_param
import ngspice_con

from code_editor_window import CodeEditorWindow

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
        self.__is_enabled = True

        # Set the default window title
        self.setWindowTitle(default_title)

        # Setup the central Graph widget
        self.__graph = Graph()
        self.__graph.initialize()
        self.setCentralWidget(self.__graph)

        ui_manager = UIManager()
        ui_manager.themeChanged.connect(self.update_)

        # Setup the menu bar
        menu_bar = self.menuBar()
        simulation_menu = menu_bar.addMenu('&Simulation')
        graph_menu = menu_bar.addMenu('&Graph')

        # "Simulation">"Select Ngspice Script..."
        action = QtGui.QAction('Select Ngspice Script...', self)
        action.triggered.connect(self.browse_script_file)
        simulation_menu.addAction(action)

        # "Simulation">"Select Data..."
        action = QtGui.QAction('Select Data...', self)
        action.triggered.connect(self.browse_data_file)
        simulation_menu.addAction(action)

        simulation_menu.addSeparator()

        # "Simulation">"Enable/Disable Simulation"
        action = QtGui.QAction('Enable/Disable Simulation', self)
        action.triggered.connect(self.toggle_enabled)
        simulation_menu.addAction(action)

        # "Simulation">"Rename Title"
        action = QtGui.QAction('Rename Title', self)
        action.triggered.connect(self.rename_title)
        simulation_menu.addAction(action)

        # "Simulation">"Reset"
        action = QtGui.QAction('Reset', self)
        action.triggered.connect(self.reset)
        simulation_menu.addAction(action)

        # "Graph">"Axis Titles"
        action = QtGui.QAction('Axis Titles', self)
        action.triggered.connect(self.set_axis_titles)
        graph_menu.addAction(action)

        # "Graph">"Log Scale"
        log_scale_menu = graph_menu.addMenu('Log Scale')

        # "Graph">"Log Scale">"X"
        self.__logscale_X_action = QtGui.QAction('X', self)
        self.__logscale_X_action.triggered.connect(self.toggle_logscale_X)
        self.__logscale_X_action.setCheckable(True)
        self.__logscale_X_action.setChecked(self.__graph.logscale_X)
        log_scale_menu.addAction(self.__logscale_X_action)

        # "Graph">"Log Scale">"Y"
        self.__logscale_Y_action = QtGui.QAction('Y', self)
        self.__logscale_Y_action.triggered.connect(self.toggle_logscale_Y)
        self.__logscale_Y_action.setCheckable(True)
        self.__logscale_Y_action.setChecked(self.__graph.logscale_Y)
        log_scale_menu.addAction(self.__logscale_Y_action)

        # "Graph">"Coordinates"
        coordinates_menu = graph_menu.addMenu('Coordinates')
        self.__coordinates_actions = {}
        
        # "Graph">"Coordinates">"Cartesian"
        self.__coordinates_actions['Cartesian'] = QtGui.QAction('Cartesian', self)
        self.__coordinates_actions['Cartesian'].triggered.connect(self.set_cartesian_coordinates)

        # "Graph">"Coordinates">"Polar"
        self.__coordinates_actions['Polar'] = QtGui.QAction('Polar', self)
        self.__coordinates_actions['Polar'].triggered.connect(self.set_polar_coordinates)

        # "Graph">"Coordinates">"Smith Chart"
        self.__coordinates_actions['Smith Chart'] = QtGui.QAction('Smith Chart', self)
        self.__coordinates_actions['Smith Chart'].triggered.connect(self.set_smith_coordinates)

        for key, action in self.__coordinates_actions.items():
            action.setCheckable(True)
            action.setChecked(key == 'Cartesian')
            coordinates_menu.addAction(action)

        # Setup the status bar
        status_bar = self.statusBar()
        status_bar.setStyleSheet('QStatusBar::item { border: None; }')

        # Status bar >"Enable Simulation"
        self.__enable_checkbox = QtWidgets.QCheckBox('Enable Simulation')
        self.__enable_checkbox.setToolTip('Disabling simulation helps reduce runtime when not needed')
        self.__enable_checkbox.setChecked(self.__is_enabled)
        self.__enable_checkbox.checkStateChanged.connect(self.checkbox_state_changed)

        status_bar.addWidget(self.__enable_checkbox)

        # Status bar >"Script:"
        self.__script_edit = LineEdit()
        self.__script_edit.setToolTip('Double-click to open with an editor')
        self.__script_edit.setReadOnly(True)
        self.__script_edit.doubleClicked.connect(self.open_script_in_editor)

        status_bar.addPermanentWidget(QtWidgets.QLabel('Script:'))
        status_bar.addPermanentWidget(self.__script_edit)

        # Status bar >"Data:"
        self.__data_edit = LineEdit()
        self.__data_edit.setToolTip('Double-click to open with an editor')
        self.__data_edit.setReadOnly(True)
        self.__data_edit.doubleClicked.connect(self.open_data_in_editor)

        status_bar.addPermanentWidget(QtWidgets.QLabel('Data:'))
        status_bar.addPermanentWidget(self.__data_edit)


    @property
    def script_file(self):
        return self.__script_file


    @script_file.setter
    def script_file(self, value):
        if not isinstance(value, str):
            raise ValueError('The `script_file` property must be a str.')
        self.__script_file = value
        self.__script_edit.setText(value)


    @property
    def data_file(self):
        return self.__data_file


    @data_file.setter
    def data_file(self, value):
        if not isinstance(value, str):
            raise ValueError('The `data_file` property must be a str.')
        self.__data_file = value
        self.__data_edit.setText(value)


    @property
    def is_enabled(self):
        return self.__is_enabled


    @is_enabled.setter
    def is_enabled(self, value):
        if not isinstance(value, bool):
            raise ValueError('The `is_enabled` property must be a boolean.')
        self.__is_enabled = value
        self.__enable_checkbox.setChecked(value)


    @property
    def graph(self):
        return self.__graph


    @Slot()
    def browse_script_file(self):
        filename, type_ = QtWidgets.QFileDialog.getOpenFileName(self,\
                'Open...', '', 'SPICE Script (*.sp *.cir *.spice);;All Files (*)')
        if not filename:
            return

        self.script_file = filename
        self.update_()


    @Slot()
    def browse_data_file(self):
        filename, type_ = QtWidgets.QFileDialog.getOpenFileName(self,\
                'Open...', '', 'Text Files (*.txt);;All Files (*)')
        if not filename:
            return

        self.data_file = filename
        self.update_()

    
    @Slot()
    def toggle_enabled(self):
        self.is_enabled = not self.is_enabled
        self.update_()


    @Slot()
    def rename_title(self):
        text, ok = QtWidgets.QInputDialog.getText(self,\
                'Rename Title', 'Title:', QtWidgets.QLineEdit.Normal, self.windowTitle())

        if ok and text:
            self.setWindowTitle(text)


    @Slot()
    def reset(self):
        self.script_file = ''
        self.data_file = ''
        self.is_enabled = True

        # Reset the window title
        self.setWindowTitle(self.__default_title)

        # Reset the graph
        self.graph.coordinates = 'Cartesian'
        self.graph.logscale_X = False
        self.graph.logscale_Y = False

        self.update_()

        self.graph.setLabel(text=None, units=None, axis='bottom')
        self.graph.setLabel(text=None, units=None, axis='left')
        self.graph.setRange(xRange=(0, 1), yRange=(0, 1), padding=0)
        self.graph.enableAutoRange(x=True, y=True)


    @Slot()
    def toggle_logscale_X(self):
        self.graph.logscale_X = not self.graph.logscale_X
        self.update_()


    @Slot()
    def toggle_logscale_Y(self):
        self.graph.logscale_Y = not self.graph.logscale_Y
        self.update_()


    @Slot()
    def set_cartesian_coordinates(self):
        self.graph.coordinates = 'Cartesian'
        self.update_()


    @Slot()
    def set_polar_coordinates(self):
        self.graph.coordinates = 'Polar'
        rho_max, ok = QtWidgets.QInputDialog.getDouble(self,\
                'Polar coordinates', '\u03C1_max:', 1.0, 0.0, 1000.0, 2,\
                Qt.WindowFlags(), 0.1)
        if ok:
            self.graph.rho_max = rho_max
        self.update_()


    @Slot()
    def set_smith_coordinates(self):
        self.graph.coordinates = 'Smith Chart'
        self.update_()


    @Slot()
    def set_axis_titles(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle('Set Axis Titles')

        # X Axis
        x_title_edit = QtWidgets.QLineEdit()
        x_unit_combo = QtWidgets.QComboBox()
        x_unit_combo.setEditable(True)
        x_unit_combo.addItems(['', 'V', 'A', 'Ω', 's', 'Hz'])

        # Y axis
        y_title_edit = QtWidgets.QLineEdit()
        y_unit_combo = QtWidgets.QComboBox()
        y_unit_combo.setEditable(True)
        y_unit_combo.addItems(['', 'V', 'A', 'Ω', 's', 'Hz'])

        # Layout
        layout = QtWidgets.QGridLayout(dialog)
        layout.addWidget(QtWidgets.QLabel('X Axis Title:'), 0, 0)
        layout.addWidget(x_title_edit, 0, 1)
        layout.addWidget(QtWidgets.QLabel('Unit:'), 0, 2)
        layout.addWidget(x_unit_combo, 0, 3)
        layout.addWidget(QtWidgets.QLabel('Y Axis Title:'), 1, 0)
        layout.addWidget(y_title_edit, 1, 1)
        layout.addWidget(QtWidgets.QLabel('Unit:'), 1, 2)
        layout.addWidget(y_unit_combo, 1, 3)

        # Buttons
        button_box = QtWidgets.QDialogButtonBox(\
                QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,\
                parent=dialog)
        layout.addWidget(button_box, 2, 0, 1, 4)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)

        if dialog.exec() == QtWidgets.QDialog.Accepted:
            self.graph.setLabel(axis='bottom',\
                    text=x_title_edit.text(), units=x_unit_combo.currentText())
            self.graph.setLabel(axis='left',\
                    text=y_title_edit.text(), units=y_unit_combo.currentText())

            self.update_()


    @Slot()
    def checkbox_state_changed(self):
        self.is_enabled = self.__enable_checkbox.isChecked()
        self.update_()


    @Slot()
    def open_script_in_editor(self):
        editor = CodeEditorWindow()
        if self.script_file:
            # Open the script file in the editor
            editor.open_file(self.script_file)
        else:
            pass # Open the editor as a new file
        editor.show()


    @Slot()
    def open_data_in_editor(self):
        editor = CodeEditorWindow()
        if self.data_file:
            # Open the data file in the editor
            editor.open_file(self.data_file)
        else:
            pass # Open the editor as a new file
        editor.show()


    @Slot()
    def update_(self):
        # Update check states of the menu actions
        self.__logscale_X_action.setChecked(self.graph.logscale_X)
        self.__logscale_Y_action.setChecked(self.graph.logscale_Y)
        for key, action in self.__coordinates_actions.items():
            action.setChecked(key == self.graph.coordinates)

        if not self.is_enabled:
            return

        # Initialize graph view
        self.graph.initialize()

        try:
            # Run ngspice simulation and plot the result
            if self.script_file:
                # Write parameters to "model.txt"
                working_dir = os.path.dirname(os.path.abspath(self.script_file))
                output_file = os.path.join(working_dir, 'model.txt')
                write_param(self.__param_dict, output_file)

                # Run ngspice_con
                ngspice_con.run(self.script_file)

                # Plot the simulation result
                root, ext = os.path.splitext(self.script_file)
                result_file = root + '.txt'

                ui_manager = UIManager()
                symbol_color = 'k' if ui_manager.theme == 'Light' else 'w'

                self.graph.plot_file(\
                        result_file,\
                        symbol_pen=symbol_color,\
                        symbol_brush=symbol_color)

            # Plot the reference data
            if self.data_file:
                self.graph.plot_file(self.data_file,\
                        symbol_pen='r',\
                        symbol_brush='r')

        except Exception as e:
            print(str(e))
