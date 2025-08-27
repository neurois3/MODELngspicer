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
import sys, os
import configparser
import base64
import pyqtgraph as pg

from ui_manager import UIManager
from parameter_io import write_param, read_param
from parameter_table import ParameterTable
from simulation_panel import SimulationPanel
from code_editor_window import CodeEditorWindow

from path_utils import get_absolute_path
from app_version import app_version

class MainWindow(QtWidgets.QMainWindow):


    def __init__(self, parent=None):
        super().__init__(parent)
        self.__param_dict = {}
        self.__param_table = ParameterTable(self.__param_dict)
        self.setup_ui()
        self.setWindowTitle('MODELngspicer')
        self.resize(700, 350)

        ui_manager = UIManager()
        ui_manager.apply_theme(self)


    def setup_ui(self):
        self.__menu_bar = self.menuBar()
        file_menu = self.__menu_bar.addMenu('&File')
        view_menu = self.__menu_bar.addMenu('&View')
        help_menu = self.__menu_bar.addMenu('&Help')
        options_menu = self.__menu_bar.addMenu('&Options')

        # Central dock area
        self.__dock_widgets = []
        self.__central_dock_area = QtWidgets.QMainWindow()
        self.setCentralWidget(self.__central_dock_area)

        for i in range(0, 10):
            default_title = 'Page {:d}'.format(i+1)
            dock_widget = QtWidgets.QDockWidget(default_title, self.__central_dock_area)
            simulation_panel = SimulationPanel(self.__param_dict, default_title)

            dock_widget.setObjectName(default_title)
            dock_widget.setWidget(simulation_panel)
            simulation_panel.windowTitleChanged.connect(dock_widget.setWindowTitle)
            self.__param_table.valueChanged.connect(simulation_panel.update_)

            self.__dock_widgets.append(dock_widget)
            self.__central_dock_area.addDockWidget(Qt.TopDockWidgetArea, dock_widget)

            if i > 0:
                # Tabify the docks to the first
                self.__central_dock_area.tabifyDockWidget(self.__dock_widgets[0], dock_widget)
            if i > 4:
                # Show only "Page 1" to "Page 5", hide the others
                dock_widget.hide()

        # Raise the first dock widget
        self.__dock_widgets[0].raise_()

        # Parameter table
        dock_widget = QtWidgets.QDockWidget('Parameters', self)
        dock_widget.setObjectName('Parameters')
        dock_widget.setWidget(self.__param_table)
        self.addDockWidget(Qt.RightDockWidgetArea, dock_widget)

        # "File">"Import Params..."
        action = QtGui.QAction('&Import Params...', self)
        action.triggered.connect(self.import_parameters)
        file_menu.addAction(action)

        # "File">"Export Params..."
        action = QtGui.QAction('&Export Params...', self)
        action.triggered.connect(self.export_parameters)
        file_menu.addAction(action)

        file_menu.addSeparator()

        # "File">"Load..."
        action = QtGui.QAction('&Load...', self)
        action.triggered.connect(self.load)
        file_menu.addAction(action)

        # "File">"Save..."
        action = QtGui.QAction('&Save...', self)
        action.triggered.connect(self.save)
        file_menu.addAction(action)

        # "View">"Tiling"
        tiling_menu = view_menu.addMenu('&Tiling')

        # "View">"Tiling">"1 x 2"
        action = QtGui.QAction('1 x 2', self)
        action.triggered.connect(lambda: self.tiling_layout(1, 2))
        tiling_menu.addAction(action)

        # "View">"Tiling">"1 x 3"
        action = QtGui.QAction('1 x 3', self)
        action.triggered.connect(lambda: self.tiling_layout(1, 3))
        tiling_menu.addAction(action)

        # "View">"Tiling">"2 x 1"
        action = QtGui.QAction('2 x 1', self)
        action.triggered.connect(lambda: self.tiling_layout(2, 1))
        tiling_menu.addAction(action)

        # "View">"Tiling">"2 x 2"
        action = QtGui.QAction('2 x 2', self)
        action.triggered.connect(lambda: self.tiling_layout(2, 2))
        tiling_menu.addAction(action)

        # "View">"Tiling">"2 x 3"
        action = QtGui.QAction('2 x 3', self)
        action.triggered.connect(lambda: self.tiling_layout(2, 3))
        tiling_menu.addAction(action)

        view_menu.addSeparator()

        # "View">"Page n"
        for i in range(0, 10):
            view_menu.addAction(self.__dock_widgets[i].toggleViewAction())

        # "Help">"User Guide - English"
        action = QtGui.QAction('&User Guide - English', self)
        action.triggered.connect(self.user_guide_english)
        help_menu.addAction(action)

        # "Help">"User Guide - Japanese"
        action = QtGui.QAction('&User Guide - Japanese', self)
        action.triggered.connect(self.user_guide_japanese)
        help_menu.addAction(action)

        # "Help">"About"
        action = QtGui.QAction('&About...', self)
        action.triggered.connect(self.about)
        help_menu.addAction(action)

        # "Options">"Theme"
        theme_menu = options_menu.addMenu('&Theme')
        ui_manager = UIManager()

        # "Options">"Theme">"Light"
        self.__light_theme_action = QtGui.QAction('&Light', self)
        self.__light_theme_action.setCheckable(True)
        self.__light_theme_action.setChecked(ui_manager.theme == 'Light')
        self.__light_theme_action.triggered.connect(self.light_theme)
        theme_menu.addAction(self.__light_theme_action)

        # "Options">"Theme">"Dark"
        self.__dark_theme_action = QtGui.QAction('&Dark', self)
        self.__dark_theme_action.setCheckable(True)
        self.__dark_theme_action.setChecked(ui_manager.theme == 'Dark')
        self.__dark_theme_action.triggered.connect(self.dark_theme)
        theme_menu.addAction(self.__dark_theme_action)

        # "Options">"Code Editor"
        action = QtGui.QAction('&Code Editor', self)
        action.triggered.connect(self.open_code_editor)
        options_menu.addAction(action)


    @Slot()
    def light_theme(self):
        self.__light_theme_action.setChecked(True)
        self.__dark_theme_action.setChecked(False)

        ui_manager = UIManager()
        ui_manager.theme = 'Light'
        ui_manager.apply_theme(self)


    @Slot()
    def dark_theme(self):
        self.__light_theme_action.setChecked(False)
        self.__dark_theme_action.setChecked(True)

        ui_manager = UIManager()
        ui_manager.theme = 'Dark'
        ui_manager.apply_theme(self)


    @Slot()
    def user_guide_english(self):
        absolute_path = get_absolute_path(__file__, '../docs/MODELngspicer_User_Guide.pdf')
        url = QtCore.QUrl('file:///' + absolute_path)
        QtGui.QDesktopServices.openUrl(url)


    @Slot()
    def user_guide_japanese(self):
        absolute_path = get_absolute_path(__file__, '../docs/MODELngspicer_User_Guide_JP.pdf')
        url = QtCore.QUrl('file:///' + absolute_path)
        QtGui.QDesktopServices.openUrl(url)


    @Slot()
    def import_parameters(self):
        filename, type_ = QtWidgets.QFileDialog.getOpenFileName(self,\
                'Import Parameters', '', 'Text Files (*.txt);;All Files (*)')
        if not filename:
            return

        basename = os.path.basename(filename)
        if basename.lower() == 'model.txt':
            message_box = QtWidgets.QMessageBox()
            message_box.setIcon(QtWidgets.QMessageBox.Warning)
            message_box.setWindowTitle('Warning')
            message_box.setText(\
                    '"model.txt" will be overwriten whenever parameters are changed!\n'\
                    'Do you still want to proceed?')
            message_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            message_box.setDefaultButton(QtWidgets.QMessageBox.No)
            answer = message_box.exec()
            if answer == QtWidgets.QMessageBox.No:
                return

        read_param(self.__param_dict, filename)
        self.__param_table.display()


    @Slot()
    def export_parameters(self):
        filename, type_ = QtWidgets.QFileDialog.getSaveFileName(self,\
                'Export Parameters', '', 'Text Files (*.txt);;All Files (*)')
        if not filename:
            return

        write_param(self.__param_dict, filename)


    @Slot()
    def tiling_layout(self, rows, columns):
        dock_area = self.__central_dock_area
        docks = self.__dock_widgets

        if rows not in [1, 2]:
            return
        if columns < 1 or (rows * columns) > len(docks):
            return

        for d in docks:
            d.hide()

        # Dock widgets to be tiled on the top and bottom
        docks_top = [docks[i] for i in range(columns)]
        docks_bottom = [] if rows == 1 else [docks[i + columns] for i in range(columns)]

        # Top:
        for d in docks_top:
            dock_area.removeDockWidget(d)
            dock_area.addDockWidget(Qt.TopDockWidgetArea, d)
            d.show()

        # Bottom:
        for d in docks_bottom:
            dock_area.removeDockWidget(d)
            dock_area.addDockWidget(Qt.BottomDockWidgetArea, d)
            d.show()

        # Resize dock widgets
        equal_width = dock_area.width() // columns
        equal_height = dock_area.height() // rows
        
        dock_area.resizeDocks(docks_top, [equal_width] * len(docks_top), Qt.Horizontal)
        dock_area.resizeDocks(docks_top, [equal_height] * len(docks_top), Qt.Vertical)
        dock_area.resizeDocks(docks_bottom, [equal_width] * len(docks_bottom), Qt.Horizontal)
        dock_area.resizeDocks(docks_bottom, [equal_height] * len(docks_bottom), Qt.Vertical)


    @Slot()
    def open_code_editor(self):
        editor = CodeEditorWindow()
        editor.show()


    @Slot()
    def about(self):
        QtWidgets.QMessageBox.about(self, 'About',\
                f"""
                <h2>MODELngspicer</h2>
                <p><strong>Version:</strong> {app_version}</p>
                <p><strong>Developed by:</strong> ペE</p>
                <p>
                    <i>MODELngspicer</i> is a Python-based GUI application that streamlines<br>
                    SPICE device modeling and circuit design with interactive parameter<br>
                    control and real-time simulation.
                </p>
                <p><strong>License:</strong> GNU General Public License v3.0</p>
                <p>
                    This program is free software: you can redistribute it and/or modify<br>
                    it under the terms of the GNU General Public License as published by<br>
                    the Free Software Foundation, either version 3 of the License, or<br>
                    (at your option) any later version.
                </p>
                <p>
                    See the LICENSE file included with this project for full details.
                </p>
                <p><strong>GitHub Repository:</strong><br>
                    <a href="https://github.com/neurois3/MODELngspicer">
                    https://github.com/neurois3/MODELngspicer</a>
                </p>
                """)


    @Slot()
    def save(self):
        filename, type_ = QtWidgets.QFileDialog.getSaveFileName(self,\
                'Save', '', 'INI Files (*.ini)')
        if not filename:
            return

        config = configparser.ConfigParser()
        config.optionxform = str

        # MainWindow
        state = self.saveState()
        encoded_state = base64.b64encode(state.data()).decode('utf-8')
        config['MainWindow'] = {\
                'WindowSize'    : f'{self.width()},{self.height()}',\
                'LayoutState'   : encoded_state,\
                }

        # CentralDockArea
        state = self.__central_dock_area.saveState()
        encoded_state = base64.b64encode(state.data()).decode('utf-8')
        config['CentralDockArea'] = {\
                'LayoutState'   : encoded_state,\
                }

        # Parameters
        config['Parameters'] = { key: f'{value:.3E}' for key, value in self.__param_dict.items() }

        # Pages
        for i, dock in enumerate(self.__dock_widgets):
            simulation_panel = dock.widget()
            config[f'Page-{i+1}'] = {\
                    'Title'         : dock.windowTitle(),\
                    'Enabled'       : simulation_panel.is_enabled,\
                    'ScriptFile'    : simulation_panel.script_file,\
                    'DataFile'      : simulation_panel.data_file,\
                    'AxisTitleX'    : simulation_panel.graph.getAxis('bottom').labelText,\
                    'AxisTitleY'    : simulation_panel.graph.getAxis('left').labelText,\
                    'AxisUnitsX'    : simulation_panel.graph.getAxis('bottom').labelUnits,\
                    'AxisUnitsY'    : simulation_panel.graph.getAxis('left').labelUnits,\
                    'LogScaleX'     : simulation_panel.graph.logscale_X,\
                    'LogScaleY'     : simulation_panel.graph.logscale_Y,\
                    'Coordinates'   : simulation_panel.graph.coordinates,\
                    'MaxRadius'     : simulation_panel.graph.rho_max,\
                    }

        with open(filename, 'w') as f:
            config.write(f)


    @Slot()
    def load(self):
        filename, type_ = QtWidgets.QFileDialog.getOpenFileName(self,\
                'Load', '', 'INI Files (*.ini)')
        if not filename:
            return

        config = configparser.ConfigParser()
        config.read(filename)

        # Progress bar
        steps = 3 + len(self.__dock_widgets) # MainWindow, CentralDockArea, Parameters, and Pages
        progress = QtWidgets.QProgressDialog('Loading settings...', 'Cancel', 0, steps, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(0)

        # MainWindow
        if 'MainWindow' in config:
            if 'WindowSize' in config['MainWindow']:
                size_str = config['MainWindow']['WindowSize']
                width, height = map(int, size_str.split(','))
                self.resize(width, height)

            if 'LayoutState' in config['MainWindow']:
                encoded_state = config['MainWindow']['LayoutState']
                state = QtCore.QByteArray(base64.b64decode(encoded_state))
                self.restoreState(state)

        progress.setValue(progress.value() + 1)

        # CentralDockArea
        if 'CentralDockArea' in config:
            if 'LayoutState' in config['CentralDockArea']:
                encoded_state = config['CentralDockArea']['LayoutState']
                state = QtCore.QByteArray(base64.b64decode(encoded_state))
                self.__central_dock_area.restoreState(state)

        progress.setValue(progress.value() + 1)

        # Parameters
        if 'Parameters' in config:
            for key in config['Parameters']:
                value_str = config['Parameters'][key]
                self.__param_dict[key] = float(value_str)
                self.__param_table.display()

        progress.setValue(progress.value() + 1)

        # Pages
        for i, dock in enumerate(self.__dock_widgets):
            simulation_panel = dock.widget()
            simulation_panel.reset()
            section_str = f'Page-{i+1}'
            if section_str in config:
                value = config[section_str].get('Title')
                if value is not None:
                    simulation_panel.setWindowTitle(value)

                value = config[section_str].get('Enabled')
                if value is not None:
                    simulation_panel.is_enabled = (value == 'True')

                value = config[section_str].get('ScriptFile')
                if value is not None:
                    simulation_panel.script_file = value

                value = config[section_str].get('DataFile')
                if value is not None:
                    simulation_panel.data_file = value

                axis_title_X = config[section_str].get('AxisTitleX')
                axis_title_Y = config[section_str].get('AxisTitleY')
                axis_units_X = config[section_str].get('AxisUnitsX')
                axis_units_Y = config[section_str].get('AxisUnitsY')

                simulation_panel.graph.setLabel(text=axis_title_X, units=axis_units_X, axis='bottom')
                simulation_panel.graph.setLabel(text=axis_title_Y, units=axis_units_Y, axis='left')

                value = config[section_str].get('LogScaleX')
                if value is not None:
                    simulation_panel.graph.logscale_X = (value == 'True')

                value = config[section_str].get('LogScaleY')
                if value is not None:
                    simulation_panel.graph.logscale_Y = (value == 'True')
                
                value = config[section_str].get('Coordinates')
                if value is not None:
                    simulation_panel.graph.coordinates = value

                value = config[section_str].get('MaxRadius')
                if value is not None:
                    simulation_panel.graph.rho_max = float(value)

            # Run simulation and plot results
            simulation_panel.update_()
            progress.setValue(progress.value() + 1)

        progress.close()
