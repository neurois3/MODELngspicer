from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
from typing import override
import numpy as np

# PyQtGraph
import pyqtgraph as pg
pg.setConfigOptions(antialias=False, background='k')

class Graph(pg.PlotWidget):
    """ Graph is a custom plot widget for displaying various types of plots using PyQtGraph.

    Features:
    - Supports different plot types: Linear, Log-Log, Semi-Log X/Y, and Smith Chart.
    - Plots data from files with customizable visual styles.
    - Draws Smith chart.
    """

    def __init__(self, parent=None):
        """ Initialize the Graph widget.

        Args:
            parent (QWidget, optional): Parent widget.
        """
        super().__init__(parent)

    def initialize(self, plotType='Linear Plot'):
        """ Configure the plot based on the specified plot type.

        Supported plot types include:
        - Linear Plot: Standard linear scaling.
        - Log-Log: Logarithmic scaling for both axes.
        - Semi-Log X: Logarithmic scaling for the X-axis.
        - Semi-Log Y: Logarithmic scaling for the Y-axis.
        - Smith Chart: Plots Smith chart curves.

        Args:
            plotType (str): The type of plot to initialize.
        """
        setting_values = {\
                'Linear Plot'   : (False, False, False),\
                'Log-Log'       : (True , True , False),\
                'Semi-Log X'    : (True , False, False),\
                'Semi-Log Y'    : (False, True , False),\
                'Smith Chart'   : (False, False, True ),\
                }

        if plotType in setting_values:
            logX, logY, aspect = setting_values[plotType]
            self.clear() 
            self.setAspectLocked(aspect)
            self.setLogMode(x=logX, y=logY)
            self.showGrid(x=True, y=True, alpha=0.3)
            if plotType == 'Smith Chart':
                self.draw_smith()

    def plot_file(self, filename, pen=None, symbol='o', symbolSize=2, symbolPen='w', symbolBrush='w'):
        """ Plot data from the specified file.

        The data file is expected to be in a format where:
        - Column 0 represents the X-axis values.
        - Subsequent columns represent Y-axis values for different data series.

        Args:
            filename (str): Path to the data file.
            pen (QPen, optional): Pen for line styling.
            symbol (str, optional): Symbol used for data points.
            symbolSize (int, optional): Size of the symbols.
            symbolPen (str, optional): Pen color for symbols.
            symbolBrush (str, optional): Brush color for symbols.
        """
        try:
            data = np.loadtxt(filename)
        except Exception:
            return

        if data.ndim == 2 and data.shape[1] > 1:
            for i in range(1, data.shape[1]):
                x = data[:, 0]
                y = data[:, i]
                self.plot(x, y,\
                        pen=pen,\
                        symbol=symbol,\
                        symbolSize=symbolSize,\
                        symbolPen=symbolPen,\
                        symbolBrush=symbolBrush)

    def draw_smith(self):
        """ Draw Smith chart curves. """

        pen = pg.mkPen(color='#808080', width=1, style=Qt.SolidLine)
        # Constant-Resistance Curves
        for ReZ in [0.0, 0.2, 0.5, 1, 2, 5, 10]:
            theta = np.linspace(0, 2*np.pi, 256)
            center = ReZ/(ReZ+1)
            radius = 1/(ReZ+1)
            self.plot(center+radius*np.cos(theta), radius*np.sin(theta), pen=pen)
    
        # Constant-Reactance Curves
        for ImZ in [0.2, 0.5, 1, 2, 5]:
            Zc = 1j*ImZ
            theta_start = np.mod(np.angle((1/Zc-1)/(Zc+1)), 2*np.pi)
            theta = np.linspace(theta_start, 1.5*np.pi, 256)
            radius = 1/ImZ
            self.plot(1+radius*np.cos(theta),  radius+radius*np.sin(theta), pen=pen)
            self.plot(1+radius*np.cos(theta), -radius-radius*np.sin(theta), pen=pen)
