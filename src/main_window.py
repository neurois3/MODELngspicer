from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
from typing import override
import sys, os

from ui_theme import apply_theme
from path_utils import *

from parameter_items import ParameterItems
from parameter_table import ParameterTable
from simulation_widget import SimulationWidget
from pop_tab import PopTab

class MainWindow(QtWidgets.QMainWindow):

    m_map_action : dict
    m_items : ParameterItems
    m_table : ParameterTable

    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_map_action = {}
        self.m_items = ParameterItems()
        self.m_table = ParameterTable(self.m_items)

        self.setupActions()
        self.setupMenuBar()
        self.setupCentralWidget()
        self.setupDockWidgets()

        self.setWindowTitle('ModelNgspicer')
        self.resize(700, 500)
        apply_theme(self)

    def setupActions(self):
        act = QtGui.QAction('&Load Parameters...', self)
        act.triggered.connect(self.loadEvent)
        self.addAction(act)

        act = QtGui.QAction('&Save Parameters...', self)
        act.triggered.connect(self.saveEvent)
        self.addAction(act)

        act = QtGui.QAction('&About...', self)
        act.triggered.connect(self.aboutEvent)
        self.addAction(act)

        act = QtGui.QAction('&User Guide - English', self)
        act.triggered.connect(\
                lambda: QtGui.QDesktopServices.openUrl(QtCore.QUrl(\
                'file:///'+get_absolute_path(__file__,\
                '../docs/ModelNgspicer_User_Guide.pdf'))))
        self.addAction(act)

        act = QtGui.QAction('&User Guide - Japanese', self)
        act.triggered.connect(\
                lambda: QtGui.QDesktopServices.openUrl(QtCore.QUrl(\
                'file:///'+get_absolute_path(__file__,\
                '../docs/ModelNgspicer_User_Guide_JP.pdf'))))
        self.addAction(act)

        for action in self.actions():
            key = action.text()
            self.m_map_action[key] = action

    def setupMenuBar(self):
        menuBar = self.menuBar()

        menu = menuBar.addMenu('&File')
        menu.addAction(self.m_map_action['&Load Parameters...'])
        menu.addAction(self.m_map_action['&Save Parameters...'])

        menu = menuBar.addMenu('&Help')
        menu.addAction(self.m_map_action['&About...'])
        menu.addAction(self.m_map_action['&User Guide - English'])
        menu.addAction(self.m_map_action['&User Guide - Japanese'])

    def setupCentralWidget(self):
        popTab = PopTab()
        for index in range(1, 11):
            mainWidget = SimulationWidget(self.m_items)
            self.m_table.valueChanged.connect(mainWidget.updateEvent)
            popTab.addTab(mainWidget, 'Tab {:d}'.format(index))

        self.setCentralWidget(popTab)

    def setupDockWidgets(self):
        dock = QtWidgets.QDockWidget('Model Parameters', self)
        dock.setWidget(self.m_table)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

    @Slot()
    def loadEvent(self):
        filename, type_ = QtWidgets.QFileDialog.getOpenFileName(self,\
                'Load Parameters...', '', 'Text Files (*.txt);;All Files (*)')
        if filename:
            basename = os.path.basename(filename)
            if basename == 'model.txt':
                msg_box = QtWidgets.QMessageBox()
                msg_box.setIcon(QtWidgets.QMessageBox.Warning)
                msg_box.setWindowTitle('Warning')
                msg_box.setText('The selected file is \'model.txt\'.')
                msg_box.setInformativeText(\
                        'This application automatically overwrites \'model.txt\' '\
                        'whenever model parameters are changed.\n'\
                        'Do you still want to proceed?')
                msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                msg_box.setDefaultButton(QtWidgets.QMessageBox.No)
                result = msg_box.exec()
                if result == QtWidgets.QMessageBox.No:
                    return

            self.m_items.load(filename)
            self.m_table.display()
    
    @Slot()
    def saveEvent(self):
        filename, type_ = QtWidgets.QFileDialog.getSaveFileName(self,\
                'Save Parameters...', '', 'Text Files (*.txt);;All Files (*)')
        if filename:
            self.m_items.write(filename)

    @Slot()
    def aboutEvent(self):
        QtWidgets.QMessageBox.about(self, 'About',\
    """
    <h2>ModelNgspicer</h2>
    <p><strong>Version:</strong> 1.0.1</p>
    <p><strong>Developed by:</strong> ペE</p>
    <p>
        ModelNgspicer is a Python-based GUI application that streamlines<br>
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
        <a href="https://github.com/neurois3/ModelNgspicer">https://github.com/neurois3/ModelNgspicer</a>
    </p>
    """)

    @override
    def closeEvent(self, event):
        popTab = self.centralWidget()
        popTab.handleParentClose()
        super().closeEvent(event)
