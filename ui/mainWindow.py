import sys
from PySide6.QtWidgets import (
    QLabel, QStackedWidget, QTabWidget, QWidget, QHBoxLayout, QVBoxLayout
    )

from ui.sub_manager_ui import SubManager
from ui.new_entry_ui import EntryWidget
from ui.task_manager_ui import TaskManager
from ui.calendar_ui import CalendarUI

class MainWindow(QWidget):
    def __init__(self, viewmodel):
        super().__init__()
        self.viewmodel = viewmodel
        self.setWindowTitle("Studio Tracker")

        self.layout = QHBoxLayout(self)

        self.tabs = QTabWidget()
        self.entryTab = EntryWidget(viewmodel=self.viewmodel)
        self.subManagerTab = SubManager(viewmodel=self.viewmodel)
        self.taskManagerTab = TaskManager(viewmodel=self.viewmodel)
        self.calendarTab = CalendarUI(viewmodel=self.viewmodel)


        self.tabs.addTab(self.entryTab, "Nuova sessione")
        self.tabs.addTab(self.subManagerTab, "Gestione materie")
        self.tabs.addTab(self.taskManagerTab, "Gestione attività")
        self.tabs.addTab(self.calendarTab, "Calendario")

        self.layout.addWidget(self.tabs)