from PySide6 import QtCore, QtGui
from path_utils import get_absolute_path

class UIManager(QtCore.QObject):
    """ Singleton class for managing UI appearance """


    themeChanged = QtCore.Signal(str) # Signal emitted when theme changes


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
