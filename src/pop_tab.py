from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
from typing import override
import sys, os

from ui_theme import apply_theme

class PopTab(QtWidgets.QTabWidget):
    """ PopTab extends QTabWidget to provide enhanced tab management functionality.

    Features:
        - Rename tabs via a dialog.
        - Pop out tabs into separate windows for individual display.
        - Restore popped-out tabs to their original place.
    """
    
    # Dictionary to track all popped-out windows indexed by tab index
    m_popoutWindows = {}

    def __init__(self, parent=None):
        """ Initialize PopTab with custom context menu and double-click functionality.

        Args:
            parent (QWidget, optional): Parent widget.
        """
        super().__init__(parent)
        self.tabBarDoubleClicked.connect(self.renameTabEvent)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.contextMenuEvent)

    @Slot()
    def renameTabEvent(self, index):
        """ Rename the tab at the given index.

        Opens a dialog to input the new name and updates the tab text.

        Args:
            index (int): Index of the tab to be renamed.
        """
        text, ok = QtWidgets.QInputDialog.getText(self, 'Rename Tab', 'Tab Name:')
        if ok and text:
            self.setTabText(index, text)
            if index in self.m_popoutWindows:
                self.m_popoutWindows[index].setWindowTitle(text)

    @Slot()
    def popOutEvent(self, index):
        """ Pop out the tab at the given index into a separate window.

        Args:
            index (int): Index of the tab to pop out.
        """
        dummy = QtWidgets.QLabel('This tab is currently popped out.')
        dummy.setAlignment(Qt.AlignCenter)
        dummy.setStyleSheet('color: red;')

        original = self.widget(index)
        text = self.tabText(index)

        self.removeTab(index)
        self.insertTab(index, dummy, text)
        self.setCurrentIndex(index)

        popoutWindow = PopoutWindow(self)
        popoutWindow.setWindowTitle(text)
        popoutWindow.setCentralWidget(original)
        popoutWindow.setAttribute(Qt.WA_DeleteOnClose)
        apply_theme(popoutWindow)

        self.m_popoutWindows[index] = popoutWindow
        
        original.show() # Make the original widget visible again
        popoutWindow.show()

    @Slot()
    def popInEvent(self, index):
        """ Restore a tab from its popped-out window.

        Args:
            index (int): Index of the popped-out tab.
        """
        self.m_popoutWindows[index].close()

    @Slot()
    def contextMenuEvent(self, pos:QtCore.QPoint):
        """ Display a context menu for the tab at the given position.

        Args:
            pos (QtCore.QPoint): Position where the context menu is displayed.
        """
        index = self.identifyTabIndex(pos)
        if index < 0:
            return

        menu = QtWidgets.QMenu(self)
        action = menu.addAction('Rename Tab')
        action.triggered.connect(lambda: self.renameTabEvent(index))

        if index in self.m_popoutWindows:
            action = menu.addAction('Pop In')
            action.triggered.connect(lambda: self.popInEvent(index))
        else:
            action = menu.addAction('Pop Out')
            action.triggered.connect(lambda: self.popOutEvent(index))

        menu.exec(self.mapToGlobal(pos))

    def identifyTabIndex(self, pos:QtCore.QPoint):
        """ Identify the tab index based on the given position.

        Args:
            pos (QtCore.QPoint): Position to check for a tab.

        Returns:
            int: Index of the tab, or -1 if no tab is found.
        """
        clickpos = self.mapToGlobal(pos)
        tabBar = self.tabBar()
        for index in range(tabBar.count()):
            if tabBar.tabRect(index).contains(tabBar.mapFromGlobal(clickpos)):
                return index;
        return -1

    def handleParentClose(self):
        """ Handle the closure of the parent window.

        This function ensures that pop-out windows are properly closed.
        """
        windows = list(self.m_popoutWindows.values())
        for window in windows:
            window.close()



class PopoutWindow(QtWidgets.QMainWindow):
    """ PopoutWindow displays a popped-out tab and restores it to the original
        widget upon closing. """
    
    # Reference to the parent PopTab instance
    m_homeTab : PopTab

    def __init__(self, parent):
        """ Initialize a PopoutWindow instance.

        Args:
            parent (PopTab): The parent PopTab instance.
        """
        super().__init__()
        self.m_homeTab = parent
    
    @override
    def closeEvent(self, event):
        """ Restore the tab to its original state upon closing the window.

        Args:
            event (QCloseEvent): The close event.
        """
        original = self.centralWidget()
        text = self.windowTitle()

        d = self.m_homeTab.m_popoutWindows
        index = [i for i, win in d.items() if win == self]
        index = index[0]

        self.m_homeTab.removeTab(index)
        self.m_homeTab.insertTab(index, original, text)
        self.m_homeTab.setCurrentIndex(index)
        self.m_homeTab.m_popoutWindows.pop(index)
        super().closeEvent(event)
