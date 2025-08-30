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
from parameter_io import ParameterIO
from parameter_table import ParameterTable
from simulation_panel import SimulationPanel
from code_editor_window import CodeEditorWindow

from path_utils import resolvePath
from app_version import APP_VERSION

class MainWindow(QtWidgets.QMainWindow):


    def __init__(self, parent=None):
        super().__init__(parent)
        self.__param_dict = {}
        self.__param_table = ParameterTable(self.__param_dict)
        self.setupUI()
        self.setWindowTitle('MODELngspicer')
        self.resize(700, 350)

        ui_manager = UIManager()
        ui_manager.applyTheme(self)


    def setupUI(self):
        # Central dock area
        self.__central_docks = []
        self.__central_dock_area = QtWidgets.QMainWindow()
        self.setCentralWidget(self.__central_dock_area)

        for i in range(0, 10):
            name = f"Page {i+1}"
            dock = QtWidgets.QDockWidget(name, self.__central_dock_area)
            content = SimulationPanel(self.__param_dict, name)

            dock.setObjectName(name)
            dock.setWidget(content)
            content.windowTitleChanged.connect(dock.setWindowTitle)
            self.__param_table.valueChanged.connect(content.update_)

            self.__central_docks.append(dock)
            self.__central_dock_area.addDockWidget(Qt.TopDockWidgetArea, dock)

            if i > 0:
                # Tabify the docks to the first
                self.__central_dock_area.tabifyDockWidget(self.__central_docks[0], dock)
            if i > 4:
                # Show only "Page 1" to "Page 5", hide the others
                dock.hide()

        # Raise the first dock widget
        self.__central_docks[0].raise_()

        # Parameter table
        dock = QtWidgets.QDockWidget('Parameters', self)
        dock.setObjectName('Parameters')
        dock.setWidget(self.__param_table)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

        # Menus
        FILE_menu = self.menuBar().addMenu('&File')
        VIEW_menu = self.menuBar().addMenu('&View')
        HELP_menu = self.menuBar().addMenu('&Help')
        OPTIONS_menu = self.menuBar().addMenu('&Options')

        # "File">"Import Params..."
        action = QtGui.QAction('&Import Params...', self)
        action.triggered.connect(self.importParameters)
        FILE_menu.addAction(action)

        # "File">"Export Params..."
        action = QtGui.QAction('&Export Params...', self)
        action.triggered.connect(self.exportParameters)
        FILE_menu.addAction(action)

        FILE_menu.addSeparator()

        # "File">"Load..."
        action = QtGui.QAction('&Load...', self)
        action.triggered.connect(self.load)
        FILE_menu.addAction(action)

        # "File">"Save..."
        action = QtGui.QAction('&Save...', self)
        action.triggered.connect(self.save)
        FILE_menu.addAction(action)

        # "View">"Tiling"
        TILING_menu = VIEW_menu.addMenu('&Tiling')

        # "View">"Tiling">"1 x 2"
        action = QtGui.QAction('1 x 2', self)
        action.triggered.connect(lambda: self.tilingLayout(1, 2))
        TILING_menu.addAction(action)

        # "View">"Tiling">"1 x 3"
        action = QtGui.QAction('1 x 3', self)
        action.triggered.connect(lambda: self.tilingLayout(1, 3))
        TILING_menu.addAction(action)

        # "View">"Tiling">"2 x 1"
        action = QtGui.QAction('2 x 1', self)
        action.triggered.connect(lambda: self.tilingLayout(2, 1))
        TILING_menu.addAction(action)

        # "View">"Tiling">"2 x 2"
        action = QtGui.QAction('2 x 2', self)
        action.triggered.connect(lambda: self.tilingLayout(2, 2))
        TILING_menu.addAction(action)

        # "View">"Tiling">"2 x 3"
        action = QtGui.QAction('2 x 3', self)
        action.triggered.connect(lambda: self.tilingLayout(2, 3))
        TILING_menu.addAction(action)

        VIEW_menu.addSeparator()

        # "View">"Page n"
        for i in range(0, 10):
            VIEW_menu.addAction(self.__central_docks[i].toggleViewAction())

        # "Help">"User Guide - English"
        action = QtGui.QAction('&User Guide - English', self)
        action.triggered.connect(self.openUserGuide_EN)
        HELP_menu.addAction(action)

        # "Help">"User Guide - Japanese"
        action = QtGui.QAction('&User Guide - Japanese', self)
        action.triggered.connect(self.openUserGuide_JP)
        HELP_menu.addAction(action)

        # "Help">"About"
        action = QtGui.QAction('&About...', self)
        action.triggered.connect(self.about)
        HELP_menu.addAction(action)

        # "Options">"Theme"
        THEME_menu = OPTIONS_menu.addMenu('&Theme')
        ui_manager = UIManager()

        # "Options">"Theme">"Light"
        self.__LIGHT_THEME_action = QtGui.QAction('&Light', self)
        self.__LIGHT_THEME_action.setCheckable(True)
        self.__LIGHT_THEME_action.setChecked(ui_manager.theme() == 'Light')
        self.__LIGHT_THEME_action.triggered.connect(self.setLightTheme)
        THEME_menu.addAction(self.__LIGHT_THEME_action)

        # "Options">"Theme">"Dark"
        self.__DARK_THEME_action = QtGui.QAction('&Dark', self)
        self.__DARK_THEME_action.setCheckable(True)
        self.__DARK_THEME_action.setChecked(ui_manager.theme() == 'Dark')
        self.__DARK_THEME_action.triggered.connect(self.setDarkTheme)
        THEME_menu.addAction(self.__DARK_THEME_action)

        # "Options">"Code Editor"
        action = QtGui.QAction('&Code Editor', self)
        action.triggered.connect(self.openCodeEditor)
        OPTIONS_menu.addAction(action)


    @Slot()
    def setLightTheme(self):
        self.__LIGHT_THEME_action.setChecked(True)
        self.__DARK_THEME_action.setChecked(False)

        ui_manager = UIManager()
        ui_manager.setTheme('Light')
        ui_manager.applyTheme(self)


    @Slot()
    def setDarkTheme(self):
        self.__LIGHT_THEME_action.setChecked(False)
        self.__DARK_THEME_action.setChecked(True)

        ui_manager = UIManager()
        ui_manager.setTheme('Dark')
        ui_manager.applyTheme(self)


    @Slot()
    def openUserGuide_EN(self):
        absolute_path = resolvePath('<PROJECTDIR>/docs/MODELngspicer_User_Guide.pdf')
        url = QtCore.QUrl('file:///' + absolute_path)
        QtGui.QDesktopServices.openUrl(url)


    @Slot()
    def openUserGuide_JP(self):
        absolute_path = resolvePath('<PROJECTDIR>/docs/MODELngspicer_User_Guide_JP.pdf')
        url = QtCore.QUrl('file:///' + absolute_path)
        QtGui.QDesktopServices.openUrl(url)


    @Slot()
    def importParameters(self):
        file_name, type_ = QtWidgets.QFileDialog.getOpenFileName(self,\
                'Import Parameters', '', 'Text Files (*.txt);;All Files (*)')
        if not file_name:
            return

        basename = os.path.basename(file_name)
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

        parameter_io = ParameterIO()
        parameter_io.read(self.__param_dict, file_name)
        self.__param_table.update_()


    @Slot()
    def exportParameters(self):
        file_name, type_ = QtWidgets.QFileDialog.getSaveFileName(self,\
                'Export Parameters', '', 'Text Files (*.txt);;All Files (*)')
        if not file_name:
            return

        parameter_io = ParameterIO()
        parameter_io.write(self.__param_dict, file_name)


    @Slot()
    def tilingLayout(self, rows, columns):
        dock_area = self.__central_dock_area
        docks = self.__central_docks

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
    def openCodeEditor(self):
        editor = CodeEditorWindow()
        editor.show()


    @Slot()
    def about(self):
        QtWidgets.QMessageBox.about(self, 'About',\
                f"""
                <h2>MODELngspicer</h2>
                <p><strong>Version:</strong> {APP_VERSION}</p>
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
        file_name, type_ = QtWidgets.QFileDialog.getSaveFileName(self,\
                'Save Settings', '', 'INI Files (*.ini)')
        if not file_name:
            return

        config = configparser.ConfigParser()
        config.optionxform = str

        # MainWindow
        state = self.saveState()
        encoded_state = base64.b64encode(state.data()).decode('utf-8')
        config['MainWindow'] = {\
                'WindowSize'    : f'{self.width()},{self.height()}',\
                'WindowLayout'  : encoded_state,\
                }

        # CentralDockArea
        state = self.__central_dock_area.saveState()
        encoded_state = base64.b64encode(state.data()).decode('utf-8')
        config['CentralDockArea'] = {\
                'WindowLayout'  : encoded_state,\
                }

        # Parameters
        config['Parameters'] = { key: f'{value:.3E}' for key, value in self.__param_dict.items() }

        # Pages
        for i, dock in enumerate(self.__central_docks):
            content = dock.widget()
            config[f'Page-{i+1}'] = {\
                    'Title'         : content.windowTitle(),\
                    'Enabled'       : content.enabled(),\
                    'ScriptFile'    : content.scriptFile(),\
                    'DataFile'      : content.dataFile(),\
                    'AxisTitleX'    : content.graph().axisTitleX(),\
                    'AxisTitleY'    : content.graph().axisTitleY(),\
                    'AxisUnitsX'    : content.graph().axisUnitsX(),\
                    'AxisUnitsY'    : content.graph().axisUnitsY(),\
                    'LogScaleX'     : content.graph().logScaleX(),\
                    'LogScaleY'     : content.graph().logScaleY(),\
                    'Coordinates'   : content.graph().coordinates(),\
                    'PolarRadius'   : content.graph().polarRadius(),\
                    }

        with open(file_name, 'w') as f:
            config.write(f)


    @Slot()
    def load(self):
        file_name, type_ = QtWidgets.QFileDialog.getOpenFileName(self,\
                'Load Settings', '', 'INI Files (*.ini)')
        if not file_name:
            return

        config = configparser.ConfigParser()
        config.read(file_name)

        # Progress bar
        steps = 3 + len(self.__central_docks) # MainWindow, CentralDockArea, Parameters, and Pages
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

            if 'WindowLayout' in config['MainWindow']:
                encoded_state = config['MainWindow']['WindowLayout']
                state = QtCore.QByteArray(base64.b64decode(encoded_state))
                self.restoreState(state)

        progress.setValue(progress.value() + 1)

        # CentralDockArea
        if 'CentralDockArea' in config:
            if 'WindowLayout' in config['CentralDockArea']:
                encoded_state = config['CentralDockArea']['WindowLayout']
                state = QtCore.QByteArray(base64.b64decode(encoded_state))
                self.__central_dock_area.restoreState(state)

        progress.setValue(progress.value() + 1)

        # Parameters
        if 'Parameters' in config:
            for key in config['Parameters']:
                value_str = config['Parameters'][key]
                self.__param_dict[key] = float(value_str)
                self.__param_table.update_()

        progress.setValue(progress.value() + 1)

        # Pages
        for i, dock in enumerate(self.__central_docks):
            content = dock.widget()
            content.reset()
            section = f'Page-{i+1}'
            if section in config:

                if 'Title' in config[section]:
                    value = config[section]['Title']
                    content.setWindowTitle(value)

                if 'Enabled' in config[section]:
                    value = config[section]['Enabled']
                    content.setEnabled(value == 'True')

                if 'ScriptFile' in config[section]:
                    value = config[section]['ScriptFile']
                    content.setScriptFile(resolvePath(value) if value else '')

                if 'DataFile' in config[section]:
                    value = config[section]['DataFile']
                    content.setDataFile(resolvePath(value) if value else '')

                if 'LogScaleX' in config[section]:
                    value = config[section]['LogScaleX']
                    content.graph().setLogScaleX(value == 'True')

                if 'LogScaleY' in config[section]:
                    value = config[section]['LogScaleY']
                    content.graph().setLogScaleY(value == 'True')

                if 'Coordinates' in config[section]:
                    value = config[section]['Coordinates']
                    content.graph().setCoordinates(value)

                if 'PolarRadius' in config[section]:
                    value = config[section]['PolarRadius']
                    content.graph().setPolarRadius(float(value))

                if 'AxisTitleX' in config[section]:
                    value = config[section]['AxisTitleX']
                    content.graph().setAxisTitleX(value)

                if 'AxisTitleY' in config[section]:
                    value = config[section]['AxisTitleY']
                    content.graph().setAxisTitleY(value)

                if 'AxisUnitsX' in config[section]:
                    value = config[section]['AxisUnitsX']
                    content.graph().setAxisUnitsX(value)

                if 'AxisUnitsY' in config[section]:
                    value = config[section]['AxisUnitsY']
                    content.graph().setAxisUnitsY(value)

            # Run simulation and plot results
            content.update_()
            progress.setValue(progress.value() + 1)

        progress.close()
