import sys
from PySide6.QtWidgets import (
    QLabel, QStackedWidget, QTabWidget, QWidget, QHBoxLayout, QVBoxLayout
    )

from ui.sub_manager_ui import SubManager
from ui.new_entry_ui import EntryWidget

class MainWindow(QWidget):
    def __init__(self, viewmodel):
        super().__init__()
        self.viewmodel = viewmodel
        self.setWindowTitle("Studio Tracker")

        self.layout = QHBoxLayout(self)
        
        self.tabs = QTabWidget()
        self.entryTab = EntryWidget(viewmodel=self.viewmodel)
        self.subManagerTab = SubManager(viewmodel=self.viewmodel)
        

        self.tabs.addTab(self.entryTab, "Nuova sessione")
        self.tabs.addTab(self.subManagerTab, "Gestione materie")

        self.layout.addWidget(self.tabs)