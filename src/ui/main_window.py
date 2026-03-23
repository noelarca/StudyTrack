import sys
from PySide6.QtWidgets import (
    QLabel, QStackedWidget, QWidget, QHBoxLayout, QVBoxLayout, QTabBar
    )

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
