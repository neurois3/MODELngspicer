from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
from typing import override
import sys, os
import pyqtgraph as pg

from ui_manager import UIManager
from path_utils import get_absolute_path

from parameter_dictionary import ParameterDictionary
from parameter_table import ParameterTable
from simulation_plotter import SimulationPlotter


class MainWindow(QtWidgets.QMainWindow):


    m_menu_bar : QtWidgets.QMenuBar
    m_dock_widgets : list
    m_central_dock_area : QtWidgets.QMainWindow

    m_parameter_dictionary : ParameterDictionary
    m_parameter_table : ParameterTable


    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_parameter_dictionary = ParameterDictionary()
        self.m_parameter_table = ParameterTable(self.m_parameter_dictionary)
        self.setup_ui()

        ui_manager = UIManager()
        ui_manager.apply_theme(self)

        self.setWindowTitle('MODELngspicer')
        self.resize(700, 350)


    def setup_ui(self):
        self.m_menu_bar = self.menuBar()
        file_menu = self.m_menu_bar.addMenu('&File')
        view_menu = self.m_menu_bar.addMenu('&View')
        help_menu = self.m_menu_bar.addMenu('&Help')
        options_menu = self.m_menu_bar.addMenu('&Options')

        self.m_central_dock_area = QtWidgets.QMainWindow()
        self.setCentralWidget(self.m_central_dock_area)
        self.m_dock_widgets = []

        for i in range(0, 10):
            window_title = 'Page {:d}'.format(i+1)
            dock_widget = QtWidgets.QDockWidget(window_title, self.m_central_dock_area)
            simulation_plotter = SimulationPlotter(self.m_parameter_dictionary)
            dock_widget.setWidget(simulation_plotter)

            simulation_plotter.setWindowTitle(window_title)
            simulation_plotter.windowTitleChanged.connect(dock_widget.setWindowTitle)
            self.m_parameter_table.valueChanged.connect(simulation_plotter.update_)

            self.m_dock_widgets.append(dock_widget)
            self.m_central_dock_area.addDockWidget(Qt.TopDockWidgetArea, dock_widget)

            if i > 0:
                # Tabify the docks to the first
                self.m_central_dock_area.tabifyDockWidget(self.m_dock_widgets[0], dock_widget)
            if i > 4:
                # Show only "Page 1" to "Page 5", hide the others
                dock_widget.hide()

        # Raise the first dock widget
        self.m_dock_widgets[0].raise_()

        for i in range(0, 10):
            view_menu.addAction(self.m_dock_widgets[i].toggleViewAction())

        dock_widget = QtWidgets.QDockWidget('Parameters', self)
        dock_widget.setWidget(self.m_parameter_table)
        self.addDockWidget(Qt.RightDockWidgetArea, dock_widget)

        action = QtGui.QAction('&Load params...', self)
        action.triggered.connect(self.load_parameters)
        file_menu.addAction(action)

        action = QtGui.QAction('&Save params...', self)
        action.triggered.connect(self.save_parameters)
        file_menu.addAction(action)

        action = QtGui.QAction('&User Guide - English', self)
        action.triggered.connect(self.user_guide_english)
        help_menu.addAction(action)

        action = QtGui.QAction('&User Guide - Japanese', self)
        action.triggered.connect(self.user_guide_japanese)
        help_menu.addAction(action)

        action = QtGui.QAction('&About...', self)
        action.triggered.connect(self.about)
        help_menu.addAction(action)

        theme_menu = options_menu.addMenu('Theme')
        ui_manager = UIManager()

        self.m_light_theme_action = QtGui.QAction('Light', self)
        self.m_light_theme_action.setCheckable(True)
        self.m_light_theme_action.setChecked(ui_manager.theme == 'Light')
        self.m_light_theme_action.triggered.connect(self.light_theme)
        theme_menu.addAction(self.m_light_theme_action)

        self.m_dark_theme_action = QtGui.QAction('Dark', self)
        self.m_dark_theme_action.setCheckable(True)
        self.m_dark_theme_action.setChecked(ui_manager.theme == 'Dark')
        self.m_dark_theme_action.triggered.connect(self.dark_theme)
        theme_menu.addAction(self.m_dark_theme_action)


    @Slot()
    def light_theme(self):
        self.m_light_theme_action.setChecked(True)
        self.m_dark_theme_action.setChecked(False)

        ui_manager = UIManager()
        ui_manager.theme = 'Light'
        ui_manager.apply_theme(self)
        
        # Set PyQtGraph background color
        pg.setConfigOptions(antialias=False, background='w')



    @Slot()
    def dark_theme(self):
        self.m_light_theme_action.setChecked(False)
        self.m_dark_theme_action.setChecked(True)

        ui_manager = UIManager()
        ui_manager.theme = 'Dark'
        ui_manager.apply_theme(self)

        # Set PyQtGraph background color
        pg.setConfigOptions(antialias=False, background='k')


    @Slot()
    def user_guide_english(self):
        absolute_path = get_absolute_path(__file__, '../docs/ModelNgspicer_User_Guide.pdf')
        url = QtCore.QUrl('file:///' + absolute_path)
        QtGui.QDesktopServices.openUrl(url)


    @Slot()
    def user_guide_japanese(self):
        absolute_path = get_absolute_path(__file__, '../docs/ModelNgspicer_User_Guide_JP.pdf')
        url = QtCore.QUrl('file:///' + absolute_path)
        QtGui.QDesktopServices.openUrl(url)


    @Slot()
    def load_parameters(self):
        filename, type_ = QtWidgets.QFileDialog.getOpenFileName(self,\
                'Load params...', '', 'Text Files (*.txt);;All Files (*)')
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

        self.m_parameter_dictionary.load_file(filename)
        self.m_parameter_table.display()


    @Slot()
    def save_parameters(self):
        filename, type_ = QtWidgets.QFileDialog.getSaveFileName(self,\
                'Save params...', '', 'Text Files (*.txt);;All Files (*)')
        if not filename:
            return

        self.m_parameter_dictionary.write_file(filename)


    @Slot()
    def about(self):
        QtWidgets.QMessageBox.about(self, 'About',\
                """
                <h2>MODELngspicer</h2>
                <p><strong>Version:</strong> 2.0.0</p>
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
                    <a href="https://github.com/neurois3/ModelNgspicer">
                    https://github.com/neurois3/ModelNgspicer</a>
                </p>
                """)
