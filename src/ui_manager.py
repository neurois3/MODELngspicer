from PySide6 import QtCore, QtGui
from path_utils import get_absolute_path

class UIManager:
    """ Singleton class for managing UI appearance """

    __inst = None

    def __new__(cls):
        # Singletone pattern
        if cls.__inst is None:
            cls.__inst = super(UIManager, cls).__new__(cls)
            cls.__inst.__initialized = False

        return cls.__inst

    def __init__(self):
        if self.__initialized:
            return
        self.theme = 'Light'
        self.__initialized = True

        # Set up a search path for image resources (used with 'img:' prefix in Qt)
        search_path = get_absolute_path(__file__, 'resources/images')
        QtCore.QDir.addSearchPath('img', search_path)

    def apply_theme(self, widget):
        stylesheet = \
                'light_theme.qss' if self.theme == 'Light'\
                else 'dark_theme.qss'

        # Read and apply the stylesheet to the given widget
        path = get_absolute_path(__file__, 'resources/stylesheets/'+stylesheet)
        with open(path, 'r') as f:
            content = f.read()
            widget.setStyleSheet(content)
        
        # Set the application icon for the widget
        icon_path = get_absolute_path(__file__, 'resources/icons/app_icon.png')
        widget.setWindowIcon(QtGui.QIcon(icon_path))
