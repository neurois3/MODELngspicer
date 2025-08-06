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

        act = QtGui.QAction('&About', self)
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
        menu.addAction(self.m_map_action['&About'])
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
                <h1>ModelNgspicer</h1>
                <p>Version 1.0.0 / developed by \u30DAE</p>
                <p>An application that accelerates SPICE-based device modeling with
                interactive parameter control and live simulation.</p>
                                    """)

    @override
    def closeEvent(self, event):
        popTab = self.centralWidget()
        popTab.handleParentClose()
        super().closeEvent(event)
