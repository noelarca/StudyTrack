from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget
)
from ui.components.sub_sidebar import SubSidebar
from ui.components.sub_details import SubDetails

class SubManager(QWidget):
    def __init__(self, viewmodel=None):
        super().__init__()
        self.viewmodel = viewmodel
        self.layout = QHBoxLayout(self)

        selector = SubSidebar(viewmodel=self.viewmodel)
        details = SubDetails(viewmodel=self.viewmodel)

        # When a subject is selected in the sidebar, set the details' subject (invokes the setter)
        selector.subject_selected.connect(lambda s: setattr(details, 'subject', s))
        
        self.layout.addWidget(selector)
        self.layout.addWidget(details)

        self.setLayout(self.layout)