from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
from typing import override
import sys, os

from graph import Graph
from parameter_dictionary import ParameterDictionary
import ngspice_con

class SimulationWidget(QtWidgets.QWidget):
    """ SimulationWidget serves as the central UI component for managing simulations and plotting.

    Features:
    - Enables users to load SPICE simulation scripts and data files.
    - Provides options for different plot types (e.g., Linear, Log-Log).
    - Manages simulation execution and visualizes results with the Graph widget.
    """
    
    m_check_box1 : QtWidgets.QCheckBox # Enable Simulation checkbox
    m_combo_box1 : QtWidgets.QComboBox # Plot type selection dropdown
    m_line_edit1 : QtWidgets.QLineEdit # Input field for simulation script
    m_line_edit2 : QtWidgets.QLineEdit # Input field for data file
    m_push_button1 : QtWidgets.QPushButton # Browse button for simulation script
    m_push_button2 : QtWidgets.QPushButton # Browse button for data file
    m_graph : Graph # Graph widget for plotting
    m_parameter_dictionary : ParameterDictionary # Reference to model parameters

    def __init__(self, parameter_dictionary, parent=None):
        """ Initialize SimulationWidget with UI elements and set up connections.

        Args:
            parameter_dictionary (ParameterDictionary): Reference to the model parameters.
            parent (QWidget, optional): Parent widget.
        """
        super().__init__(parent)
        
        # Initialize UI components
        self.m_check_box1 = QtWidgets.QCheckBox('Enable Simulation')
        self.m_combo_box1 = QtWidgets.QComboBox()
        self.m_line_edit1 = QtWidgets.QLineEdit()
        self.m_line_edit2 = QtWidgets.QLineEdit()
        self.m_push_button1 = QtWidgets.QPushButton('Browse')
        self.m_push_button2 = QtWidgets.QPushButton('Browse')
        self.m_graph = Graph()
        self.m_parameter_dictionary = parameter_dictionary

        # Set default states and connect signals
        self.m_check_box1.setCheckState(Qt.Checked)
        self.m_check_box1.checkStateChanged.connect(self.update_)
        self.m_line_edit1.setReadOnly(True)
        self.m_line_edit2.setReadOnly(True)
        self.m_push_button1.clicked.connect(self.browse_script_file)
        self.m_push_button2.clicked.connect(self.browse_data_file)
        self.m_combo_box1.addItems(\
                ['Linear Plot', 'Log-Log', 'Semi-Log X', 'Semi-Log Y', 'Smith Chart'])
        self.m_combo_box1.currentTextChanged.connect(self.update_)
        self.m_graph.initialize()

        # Layout setup
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.m_check_box1)
        hbox.addWidget(self.m_combo_box1)
        hbox.setContentsMargins(3, 3, 3, 3)

        grid = QtWidgets.QGridLayout()
        row = 0
        grid.addWidget(QtWidgets.QLabel('Simulation Script:'), row, 0)
        grid.addWidget(self.m_line_edit1, row, 1)
        grid.addWidget(self.m_push_button1, row, 2)
        row = 1
        grid.addWidget(QtWidgets.QLabel('Data File:'), row, 0)
        grid.addWidget(self.m_line_edit2, row, 1)
        grid.addWidget(self.m_push_button2, row, 2)

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setSpacing(3)
        vbox.addLayout(hbox)
        vbox.addLayout(grid)
        vbox.addWidget(self.m_graph)

    @Slot()
    def update_(self):
        """ Update the state of the simulation and plot the results.

        - Runs the SPICE simulation if a script is provided.
        - Visualizes data from the simulation and/or data file.
        """
        enabled = (self.m_check_box1.checkState() == Qt.Checked)
        script_name = self.m_line_edit1.text()
        if not enabled or not script_name:
            return

        try:
            # Write model parameters to "model.txt"
            working_dir = os.path.dirname(os.path.abspath(script_name))
            self.m_parameter_dictionary.write_file(os.path.join(working_dir, 'model.txt'))

            # Run Ngspice simulation and plot result
            plot_type = self.m_combo_box1.currentText()
            self.m_graph.initialize(plot_type)

            if script_name:
                ngspice_con.run(script_name)
                root, ext = os.path.splitext(script_name)
                result_name = root + '.txt'
                self.m_graph.plot_file(result_name, symbolPen='w', symbolBrush='w')

            # Plot data file
            data_name = self.m_line_edit2.text()
            if data_name:
                self.m_graph.plot_file(data_name, symbolPen='r', symbolBrush='r')

        except Exception as e:
            print(str(e))

    @Slot()
    def browse_script_file(self):
        """ Browse for a SPICE simulation script and update the input field. """

        filename, type_ = QtWidgets.QFileDialog.getOpenFileName(self,\
                'Open...', '', 'SPICE Script (*.sp *.cir *.spice);;All Files (*)')
        if filename:
            self.m_line_edit1.setText(filename)
            self.update_()

    @Slot()
    def browse_data_file(self):
        """ Browse for a data file and update the input field. """

        filename, type_ = QtWidgets.QFileDialog.getOpenFileName(self,\
                'Open...', '', 'Text Files (*.txt);;All Files (*)')
        if filename:
            self.m_line_edit2.setText(filename)
            self.update_()
