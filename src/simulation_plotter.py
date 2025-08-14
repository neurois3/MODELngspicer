# Copyright (C) 2025 ペE(neuroi3)
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
from parameter_dictionary import ParameterDictionary
import ngspice_con


class LineEdit(QtWidgets.QLineEdit):
    """A custom QLineEdit that emits a signal upon double-clicking."""

    # Signal emitted when double-clicked
    doubleClicked = Signal()

    @override
    def mouseDoubleClickEvent(self, event):
        self.doubleClicked.emit()


class SimulationPlotter(QtWidgets.QMainWindow):


    def __init__(self, parameter_dictionary, parent=None):
        super().__init__(parent)

        self.m_parameter_dictionary = parameter_dictionary
        self.m_script_filename = '' # Path to a simulation script file
        self.m_data_filename = '' # Path to a data file
        self.m_enabled_state = True

        # Setup the central Graph widget
        self.m_graph = Graph()
        self.m_graph.initialize()
        self.setCentralWidget(self.m_graph)

        self.ui_manager = UIManager()
        self.ui_manager.themeChanged.connect(self.update_)

        # Setup the menu bar
        menu_bar = self.menuBar()
        simulation_menu = menu_bar.addMenu('&Simulation')
        graph_menu = menu_bar.addMenu('&Graph')

        # "Simulation">"Select ngspice script..."
        action = QtGui.QAction('Select ngspice script...', self)
        action.triggered.connect(self.browse_script_file)
        simulation_menu.addAction(action)

        # "Simulation">"Select data file..."
        action = QtGui.QAction('Select data file...', self)
        action.triggered.connect(self.browse_data_file)
        simulation_menu.addAction(action)

        simulation_menu.addSeparator()

        # "Simulation">"Enable/disable simulation"
        action = QtGui.QAction('Enable/disable simulation', self)
        action.triggered.connect(self.toggle_enabled_state)
        simulation_menu.addAction(action)

        # "Simulation">"Rename title"
        action = QtGui.QAction('Rename title', self)
        action.triggered.connect(self.rename_title)
        simulation_menu.addAction(action)

        # "Simulation">"Reset"
        action = QtGui.QAction('Reset', self)
        action.triggered.connect(self.reset)
        simulation_menu.addAction(action)

        # "Graph">"Axis titles"
        action = QtGui.QAction('Axis titles', self)
        action.triggered.connect(self.set_axis_titles)
        graph_menu.addAction(action)

        # "Graph">"Log scale"
        log_scale_menu = graph_menu.addMenu('Log scale')

        # "Graph">"Log scale">"X"
        self.m_log_X_action = QtGui.QAction('X', self)
        self.m_log_X_action.triggered.connect(self.toggle_log_X)
        self.m_log_X_action.setCheckable(True)
        self.m_log_X_action.setChecked(self.m_graph.log_X)
        log_scale_menu.addAction(self.m_log_X_action)

        # "Graph">"Log scale">"Y"
        self.m_log_Y_action = QtGui.QAction('Y', self)
        self.m_log_Y_action.triggered.connect(self.toggle_log_Y)
        self.m_log_Y_action.setCheckable(True)
        self.m_log_Y_action.setChecked(self.m_graph.log_Y)
        log_scale_menu.addAction(self.m_log_Y_action)

        # "Graph">"Coordinates"
        coordinates_menu = graph_menu.addMenu('Coordinates')
        self.m_coordinates_actions = {}
        
        # "Graph">"Coordinates">"Cartesian"
        self.m_coordinates_actions['Cartesian'] = QtGui.QAction('Cartesian', self)
        self.m_coordinates_actions['Cartesian'].triggered.connect(self.set_cartesian_coordinates)

        # "Graph">"Coordinates">"Polar"
        self.m_coordinates_actions['Polar'] = QtGui.QAction('Polar', self)
        self.m_coordinates_actions['Polar'].triggered.connect(self.set_polar_coordinates)

        # "Graph">"Coordinates">"Smith chart"
        self.m_coordinates_actions['Smith chart'] = QtGui.QAction('Smith chart', self)
        self.m_coordinates_actions['Smith chart'].triggered.connect(self.set_smith_coordinates)

        for key, action in self.m_coordinates_actions.items():
            action.setCheckable(True)
            action.setChecked(key == 'Cartesian')
            coordinates_menu.addAction(action)

        # Setup the status bar
        status_bar = self.statusBar()
        status_bar.setStyleSheet('QStatusBar::item { border: None; }')

        # Status bar >"Enable simulation"
        self.m_enable_simulation_check_box = QtWidgets.QCheckBox('Enable simulation')
        self.m_enable_simulation_check_box.setChecked(self.m_enabled_state)
        self.m_enable_simulation_check_box.checkStateChanged.connect(self.check_box_state_changed)
        status_bar.addWidget(self.m_enable_simulation_check_box)

        # Status bar >"Script:"
        self.m_script_line_edit = LineEdit()
        self.m_script_line_edit.setReadOnly(True)
        self.m_script_line_edit.doubleClicked.connect(self.open_script_file_in_editor)
        status_bar.addPermanentWidget(QtWidgets.QLabel('Script:'))
        status_bar.addPermanentWidget(self.m_script_line_edit)

        # Status bar >"Data:"
        self.m_data_line_edit = LineEdit()
        self.m_data_line_edit.setReadOnly(True)
        self.m_data_line_edit.doubleClicked.connect(self.open_data_file_in_editor)
        status_bar.addPermanentWidget(QtWidgets.QLabel('Data:'))
        status_bar.addPermanentWidget(self.m_data_line_edit)


    @Slot()
    def browse_script_file(self):
        filename, type_ = QtWidgets.QFileDialog.getOpenFileName(self,\
                'Open...', '', 'SPICE Script (*.sp *.cir *.spice);;All Files (*)')
        if not filename:
            return

        self.m_script_filename = filename
        self.update_()


    @Slot()
    def browse_data_file(self):
        filename, type_ = QtWidgets.QFileDialog.getOpenFileName(self,\
                'Open...', '', 'Text Files (*.txt);;All Files (*)')
        if not filename:
            return

        self.m_data_filename = filename
        self.update_()

    
    @Slot()
    def toggle_enabled_state(self):
        self.m_enabled_state = not self.m_enabled_state
        self.update_()


    @Slot()
    def rename_title(self):
        text, ok = QtWidgets.QInputDialog.getText(self,\
                'Rename title', 'Title:', QtWidgets.QLineEdit.Normal, self.windowTitle())

        if ok and text:
            self.setWindowTitle(text)


    @Slot()
    def reset(self):
        self.m_script_filename = ''
        self.m_data_filename = ''
        self.m_enabled_state = True
        self.update_()


    @Slot()
    def toggle_log_X(self):
        self.m_graph.log_X = not self.m_graph.log_X
        self.update_()


    @Slot()
    def toggle_log_Y(self):
        self.m_graph.log_Y = not self.m_graph.log_Y
        self.update_()


    @Slot()
    def set_cartesian_coordinates(self):
        self.m_graph.coordinates = 'Cartesian'
        self.update_()


    @Slot()
    def set_polar_coordinates(self):
        self.m_graph.coordinates = 'Polar'
        rho_max, ok = QtWidgets.QInputDialog.getDouble(self,\
                'Polar coordinates', '\u03C1_max:', 1.0, 0.0, 1000.0, 2,\
                Qt.WindowFlags(), 0.1)
        if ok:
            self.m_graph.rho_max = rho_max

        self.update_()


    @Slot()
    def set_smith_coordinates(self):
        self.m_graph.coordinates = 'Smith chart'
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
            self.m_graph.setLabel(axis='bottom',\
                    text=x_title_edit.text(), units=x_unit_combo.currentText())
            self.m_graph.setLabel(axis='left',\
                    text=y_title_edit.text(), units=y_unit_combo.currentText())

            self.update_()


    @Slot()
    def check_box_state_changed(self):
        self.m_enabled_state = self.m_enable_simulation_check_box.isChecked()
        self.update_()


    @Slot()
    def open_script_file_in_editor(self):
        # Open the script file with a custom text editor
        # To be implemented
        print('double clicked')


    @Slot()
    def open_data_file_in_editor(self):
        # Open the data file with a custom text editor
        # To be implemented
        print('double clicked')


    @Slot()
    def update_(self):
        # Update texts in the line edits
        self.m_script_line_edit.setText(self.m_script_filename)
        self.m_data_line_edit.setText(self.m_data_filename)

        # Change the state of "Enable simulation" check box
        self.m_enable_simulation_check_box.setChecked(self.m_enabled_state)

        # Update check states of the menu actions
        self.m_log_X_action.setChecked(self.m_graph.log_X)
        self.m_log_Y_action.setChecked(self.m_graph.log_Y)
        for key, action in self.m_coordinates_actions.items():
            action.setChecked(key == self.m_graph.coordinates)

        if not self.m_enabled_state:
            return

        # Initialize graph view
        self.m_graph.initialize()

        try:
            # Run ngspice simulation and plot the result
            if self.m_script_filename:
                # Write parameters to "model.txt"
                working_dir = os.path.dirname(os.path.abspath(self.m_script_filename))
                output_filename = os.path.join(working_dir, 'model.txt')
                self.m_parameter_dictionary.write_file(output_filename)

                # Run ngspice_con
                ngspice_con.run(self.m_script_filename)

                # Plot the simulation result
                root, ext = os.path.splitext(self.m_script_filename)
                result_filename = root + '.txt'

                theme = self.ui_manager.theme
                symbol_color = 'k' if theme == 'Light' else 'w'

                self.m_graph.plot_file(result_filename,\
                        symbol_pen=symbol_color,\
                        symbol_brush=symbol_color)

            # Plot the reference data
            if self.m_data_filename:
                self.m_graph.plot_file(self.m_data_filename,\
                        symbol_pen='r',\
                        symbol_brush='r')

        except Exception as e:
            print(str(e))
