from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
from typing import override
import sys, os

from graph import Graph
from parameter_items import ParameterItems
import ngspice_con

class SimulationWidget(QtWidgets.QWidget):
    """ SimulationWidget serves as the central UI component for managing simulations and plotting.

    Features:
    - Enables users to load SPICE simulation scripts and data files.
    - Provides options for different plot types (e.g., Linear, Log-Log).
    - Manages simulation execution and visualizes results with the Graph widget.
    """
    
    m_checkBox1     : QtWidgets.QCheckBox # Enable Simulation checkbox
    m_comboBox1     : QtWidgets.QComboBox # Plot type selection dropdown
    m_lineEdit1     : QtWidgets.QLineEdit # Input field for simulation script
    m_lineEdit2     : QtWidgets.QLineEdit # Input field for data file
    m_pushButton1   : QtWidgets.QPushButton # Browse button for simulation script
    m_pushButton2   : QtWidgets.QPushButton # Browse button for data file
    m_Graph         : Graph # Graph widget for plotting
    m_items         : ParameterItems # Reference to model parameters

    def __init__(self, items, parent=None):
        """ Initialize SimulationWidget with UI elements and set up connections.

        Args:
            items (ParameterItems): Reference to the model parameters.
            parent (QWidget, optional): Parent widget.
        """
        super().__init__(parent)
        
        # Initialize UI components
        self.m_checkBox1    = QtWidgets.QCheckBox('Enable Simulation')
        self.m_comboBox1    = QtWidgets.QComboBox()
        self.m_lineEdit1    = QtWidgets.QLineEdit()
        self.m_lineEdit2    = QtWidgets.QLineEdit()
        self.m_pushButton1  = QtWidgets.QPushButton('Browse')
        self.m_pushButton2  = QtWidgets.QPushButton('Browse')
        self.m_Graph        = Graph()
        self.m_items        = items

        # Set default states and connect signals
        self.m_checkBox1.setCheckState(Qt.Checked)
        self.m_checkBox1.checkStateChanged.connect(self.updateEvent)
        self.m_lineEdit1.setReadOnly(True)
        self.m_lineEdit2.setReadOnly(True)
        self.m_pushButton1.clicked.connect(self.browseEvent1)
        self.m_pushButton2.clicked.connect(self.browseEvent2)
        self.m_comboBox1.addItems(\
                ['Linear Plot', 'Log-Log', 'Semi-Log X', 'Semi-Log Y', 'Smith Chart'])
        self.m_comboBox1.currentTextChanged.connect(self.updateEvent)
        self.m_Graph.initialize()

        # Layout setup
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.m_checkBox1)
        hbox.addWidget(self.m_comboBox1)
        hbox.setContentsMargins(3, 3, 3, 3)

        grid = QtWidgets.QGridLayout()
        row = 0
        grid.addWidget(QtWidgets.QLabel('Simulation Script:'), row, 0)
        grid.addWidget(self.m_lineEdit1, row, 1)
        grid.addWidget(self.m_pushButton1, row, 2)
        row = 1
        grid.addWidget(QtWidgets.QLabel('Data File:'), row, 0)
        grid.addWidget(self.m_lineEdit2, row, 1)
        grid.addWidget(self.m_pushButton2, row, 2)

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setSpacing(3)
        vbox.addLayout(hbox)
        vbox.addLayout(grid)
        vbox.addWidget(self.m_Graph)

    @Slot()
    def updateEvent(self):
        """ Update the state of the simulation and plot the results.

        - Runs the SPICE simulation if a script is provided.
        - Visualizes data from the simulation and/or data file.
        """
        enabled = (self.m_checkBox1.checkState() == Qt.Checked)
        scriptname = self.m_lineEdit1.text()
        if not enabled or not scriptname:
            return

        try:
            # Write model parameters to "model.txt"
            workingdir = os.path.dirname(os.path.abspath(scriptname))
            self.m_items.write(os.path.join(workingdir, 'model.txt'))

            # Run Ngspice simulation and plot result
            plotType = self.m_comboBox1.currentText()
            self.m_Graph.initialize(plotType)

            if scriptname:
                ngspice_con.run(scriptname)
                root, ext = os.path.splitext(scriptname)
                resultname = root + '.txt'
                self.m_Graph.plot_file(resultname, symbolPen='w', symbolBrush='w')

            # Plot data file
            dataname = self.m_lineEdit2.text()
            if dataname:
                self.m_Graph.plot_file(dataname, symbolPen='r', symbolBrush='r')

        except Exception as e:
            print(str(e))

    @Slot()
    def browseEvent1(self):
        """ Browse for a SPICE simulation script and update the input field. """

        filename, type_ = QtWidgets.QFileDialog.getOpenFileName(self,\
                'Open...', '', 'SPICE Script (*.sp *.cir *.spice);;All Files (*)')
        if filename:
            self.m_lineEdit1.setText(filename)
            self.updateEvent()

    @Slot()
    def browseEvent2(self):
        """ Browse for a data file and update the input field. """

        filename, type_ = QtWidgets.QFileDialog.getOpenFileName(self,\
                'Open...', '', 'Text Files (*.txt);;All Files (*)')
        if filename:
            self.m_lineEdit2.setText(filename)
            self.updateEvent()
