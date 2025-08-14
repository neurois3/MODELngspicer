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
import numpy as np

from ui_manager import UIManager

# PyQtGraph
import pyqtgraph as pg
pg.setConfigOptions(antialias=False)


class Graph(pg.PlotWidget):


    def __init__(self, parent=None):
        super().__init__(parent)

        self.log_X = False
        self.log_Y = False
        self.coordinates = 'Cartesian' # or 'Polar' or 'Smith chart'
        self.rho_max = 1.0 # Maximum radius for 'Polar' plot


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

        # Constant-resistance curves
        for Re_Z in [0.0, 0.2, 0.5, 1, 2, 5, 10]:
            theta = np.linspace(0, 2*np.pi, 256)
            center = Re_Z/(Re_Z+1)
            radius = 1/(Re_Z+1)

            self.plot(center+radius*np.cos(theta), radius*np.sin(theta), pen=pen)
    
        # Constant-reactance curves
        for Im_Z in [0.2, 0.5, 1, 2, 5]:
            Zc = 1j*Im_Z
            theta_start = np.mod(np.angle((1/Zc-1)/(Zc+1)), 2*np.pi)
            theta = np.linspace(theta_start, 1.5*np.pi, 256)
            radius = 1/Im_Z

            self.plot(1+radius*np.cos(theta),  radius+radius*np.sin(theta), pen=pen)
            self.plot(1+radius*np.cos(theta), -radius-radius*np.sin(theta), pen=pen)


    def draw_polar(self):
        pen = pg.mkPen(color='#808080', width=1, style=Qt.SolidLine)

        # Constant-theta curves
        theta_vector = np.arange(0.0, 2*np.pi, np.pi/6)
        for theta in theta_vector:
            self.plot([0, self.rho_max*np.cos(theta)], [0, self.rho_max*np.sin(theta)], pen=pen)

        # Constant-radius curves
        rho_vector = self.rho_max*np.array([0.0, 0.25, 0.5, 0.75, 1.0])
        theta = np.linspace(0, 2*np.pi, 361)
        for rho in rho_vector:
            self.plot(rho*np.cos(theta), rho*np.sin(theta), pen=pen)
