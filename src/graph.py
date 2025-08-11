from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
import numpy as np

from ui_manager import UIManager

# PyQtGraph
import pyqtgraph as pg

class Graph(pg.PlotWidget):


    log_X = False
    log_Y = False
    coordinates = 'Cartesian' # or 'Polar' or 'Smith chart'


    def __init__(self, parent=None):
        super().__init__(parent)


    def initialize(self):
        ui_manager = UIManager()
        theme = ui_manager.theme

        # Set background color
        background_color = 'w' if theme == 'Light' else 'k'
        self.setBackground(background_color)
        
        # Clear existing plots, and set log scales and aspect ratio
        self.clear()
        aspect_lock = self.coordinates in ['Polar', 'Smith chart']
        self.setAspectLocked(aspect_lock)
        self.setLogMode(x=self.log_X, y=self.log_Y)
        self.showGrid(x=True, y=True, alpha=0.3)

        # Draw smith chart
        if self.coordinates == 'Smith chart':
            self.draw_smith()

        # Draw polar grid
        elif self.coordinates == 'Polar':
            self.draw_polar()


    def plot_file(self, filename, pen=None, symbol='o', symbol_size=2,\
            symbol_pen='w', symbol_brush='w'):
        try:
            # Load a text file
            data = np.loadtxt(filename)

        except Exception as e:
            print(str(e))
            return

        if data.ndim != 2 or data.shape[1] < 2:
            # Returns if the data is not two-dimensional or does not have
            # more than two columns
            return

        for column in range(1, data.shape[1]):
            x = data[:, 0]
            y = data[:, column]
            self.plot(x, y, pen=pen, symbol=symbol,\
                    symbolSize=symbol_size,\
                    symbolPen=symbol_pen,\
                    symbolBrush=symbol_brush)


    def draw_smith(self):
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


    def draw_polar(self):
        pen = pg.mkPen(color='#808080', width=1, style=Qt.SolidLine)
