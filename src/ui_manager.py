from PySide6 import QtCore, QtGui
from path_utils import *

# Applies a stylesheet and icon to a given widget
def apply_theme(widget, stylesheet='dark.qss'):
    # Sets up a search path for image resources
    searchpath = get_absolute_path(__file__, 'resources/images')
    QtCore.QDir.addSearchPath('img', searchpath)

    # Reads and applies the stylesheet to the widget
    stylesheet = get_absolute_path(__file__, 'resources/stylesheets/'+stylesheet)
    with open(stylesheet, 'r') as f:
        text = f.read()
        widget.setStyleSheet(text)

    # Sets the window icon
    widget.setWindowIcon(QtGui.QIcon(get_absolute_path(__file__, 'resources/icons/app_icon.png')))
