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
import time
import platform

from main_window import MainWindow
from app_version import APP_VERSION
from path_utils import resolvePath

if __name__ == '__main__':
    operating_system = platform.system()
    app_id = 'ModelNgspicer'

    if operating_system == 'Windows':
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    else:
        pass

    app = QtWidgets.QApplication(sys.argv)

    # Display the splash screen during application startup
    splash_pix = QtGui.QPixmap(resolvePath('<PROJECTDIR>/src/resources/splashscreen/splash.png'))
    splash = QtWidgets.QSplashScreen(splash_pix)
    splash.show()
    splash.showMessage(f'MODELngspicer v{APP_VERSION} - Loading...', Qt.AlignLeft, Qt.white)
    time.sleep(1)

    ex  = MainWindow()
    ex.show()

    # Close the splash screen
    splash.finish(ex)
    sys.exit(app.exec())
