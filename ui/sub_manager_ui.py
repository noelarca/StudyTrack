from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget
)
from ui.components.sub_sidebar import SubSidebar
from ui.components.sub_details import SubDetails
from ui.components.new_sub_window import NewSubjectWindow

from PySide6.QtCore import Signal

class SubManager(QWidget):
    def __init__(self, viewmodel=None):
        super().__init__()
        self.viewmodel = viewmodel
        self.layout = QHBoxLayout(self)

        selector = SubSidebar(viewmodel=self.viewmodel)
        details = SubDetails(viewmodel=self.viewmodel)

        selector.subject_selected.connect(details.load_details)
        
        self.layout.addWidget(selector)
        self.layout.addWidget(details)

        self.setLayout(self.layout)