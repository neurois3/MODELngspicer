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

from PySide6 import QtCore, QtGui
from path_utils import get_absolute_path


class UIManager(QtCore.QObject):
    """Singleton class for managing UI appearance"""

    # Signal emitted when theme changes
    themeChanged = QtCore.Signal(str)


    _inst = None

    def __new__(cls):
        if cls._inst is None:
            cls._inst = super(UIManager, cls).__new__(cls)
            cls._inst._initialized = False

        return cls._inst


    def __init__(self):
        if self._initialized:
            return

        super().__init__() # Initialize QObject

        self._theme = None
        self.theme = 'Light' # Use setter to initialize
        self._initialized = True

        # Set up a search path for image resources
        search_path = get_absolute_path(__file__, 'resources/images')
        QtCore.QDir.addSearchPath('img', search_path)

    
    @property
    def theme(self):
        return self._theme


    @theme.setter
    def theme(self, value):
        if value not in ['Light', 'Dark']:
            raise ValueError(f'Unsupported theme: {value}')

        if value != self._theme:
            self._theme = value
            self.themeChanged.emit(value) # Emit signal when theme changes


    def apply_theme(self, widget):
        stylesheet = \
                'light_theme.qss' if self.theme == 'Light'\
                else 'dark_theme.qss'

        # Read and apply the stylesheet to the given widget
        path = get_absolute_path(__file__, 'resources/stylesheets/'+stylesheet)
        try:
            with open(path, 'r') as f:
                content = f.read()
                widget.setStyleSheet(content)
        except FileNotFoundError:
            print(f'Stylesheet not found: {path}')
        
        # Set the application icon for the widget
        icon_path = get_absolute_path(__file__, 'resources/icons/app_icon.png')
        widget.setWindowIcon(QtGui.QIcon(icon_path))
