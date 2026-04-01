import sys
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTabBar,
    QSystemTrayIcon, QMenu, QStyle
    )
from PySide6.QtGui import QAction, QIcon
from utils.hotkeys import HotkeyManager

from ui.views.sub_manager_view import SubManager
from ui.views.entry_view import EntryWidget
from ui.views.task_manager_view import TaskManager
from ui.views.calendar_view import CalendarUI
from ui.views.settings_view import SettingsUI
from ui.components.common.sliding_stack import SlidingStackedWidget

class MainWindow(QWidget):
    """
    The main window of the Study Tracker application.
    It uses a QTabBar and a SlidingStackedWidget to organize different functional areas with animations.
    """
    def __init__(self, viewmodel):
        """
        Initializes the main window and its child tabs.
        
        Args:
            viewmodel (ViewModel): The viewmodel instance for data binding.
        """
        super().__init__()
        self.viewmodel = viewmodel
        self.setWindowTitle("Studio Tracker")

        # Main vertical layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(0)

        # Create tab bar
        self.tab_bar = QTabBar()
        self.tab_bar.setExpanding(True)
        self.tab_bar.addTab("Nuova sessione")
        self.tab_bar.addTab("Gestione materie")
        self.tab_bar.addTab("Gestione attività")
        self.tab_bar.addTab("Calendario")
        self.tab_bar.addTab("Impostazioni")

        # Create animated stack
        self.stack = SlidingStackedWidget()
        
        # Individual tab widgets
        self.entryTab = EntryWidget(viewmodel=self.viewmodel)
        self.subManagerTab = SubManager(viewmodel=self.viewmodel)
        self.taskManagerTab = TaskManager(viewmodel=self.viewmodel)
        self.calendarTab = CalendarUI(viewmodel=self.viewmodel)
        self.settingsTab = SettingsUI(viewmodel=self.viewmodel)

        # Add widgets to the animated stack
        self.stack.addWidget(self.entryTab)
        self.stack.addWidget(self.subManagerTab)
        self.stack.addWidget(self.taskManagerTab)
        self.stack.addWidget(self.calendarTab)
        self.stack.addWidget(self.settingsTab)

        # Connect tab bar change signal to the stack's animation method
        self.tab_bar.currentChanged.connect(self.stack.slide_to_index)

        # Add to main layout
        self.main_layout.addWidget(self.tab_bar)
        self.main_layout.addWidget(self.stack)

        # Setup Shortcuts using the manager
        HotkeyManager.setup_main_navigation(self)

        # Setup System Tray
        self.setup_tray()

    def setup_tray(self):
        """Initializes the system tray icon and its context menu."""
        self.tray_icon = QSystemTrayIcon(self)
        
        # Use a standard icon for now
        icon = self.style().standardIcon(QStyle.SP_ComputerIcon)
        self.tray_icon.setIcon(icon)
        
        # Create the menu
        tray_menu = QMenu(self)
        
        restore_action = QAction("Ripristina", self)
        restore_action.triggered.connect(self.show_and_raise)
        
        exit_action = QAction("Esci", self)
        exit_action.triggered.connect(self.force_quit)
        
        tray_menu.addAction(restore_action)
        tray_menu.addSeparator()
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.show()

    def on_tray_icon_activated(self, reason):
        """Handles double-click or single-click on the tray icon."""
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            self.show_and_raise()

    def show_and_raise(self):
        """Shows the window and brings it to the front."""
        self.showNormal()
        self.activateWindow()
        self.raise_()

    def force_quit(self):
        """Exits the application completely, bypassing the tray logic."""
        self.entryTab.save_ongoing_session()
        # Use QApplication.quit() to ensure a clean exit
        from PySide6.QtWidgets import QApplication
        QApplication.quit()

    def closeEvent(self, event):
        """
        Handles the application closure event.
        Can minimize to tray instead of closing based on settings.
        """
        if self.viewmodel.get_setting("close_to_tray"):
            self.hide()
            self.tray_icon.showMessage(
                "Studio Tracker",
                "L'applicazione è ancora in esecuzione nella barra di sistema.",
                QSystemTrayIcon.Information,
                2000
            )
            event.ignore()
        else:
            # Tell the entry tab to finalize and save any active session
            self.entryTab.save_ongoing_session()
            event.accept()
