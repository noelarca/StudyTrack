from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget
)
from ui.components.sub_sidebar import SubSidebar
from ui.components.sub_details import SubDetails

class SubManager(QWidget):
    """
    UI component for managing study subjects.
    It combines a sidebar for selecting subjects and a details view for 
    viewing and editing specific subject information.
    """
    def __init__(self, viewmodel=None):
        """
        Initializes the subject manager interface.
        
        Args:
            viewmodel (ViewModel): The viewmodel instance for data operations.
        """
        super().__init__()
        self.viewmodel = viewmodel
        
        # Horizontal layout to split sidebar and details
        self.layout = QHBoxLayout(self)

        # Initialize sidebar (selector) and details components
        selector = SubSidebar(viewmodel=self.viewmodel)
        selector.setFixedWidth(200)
        details = SubDetails(viewmodel=self.viewmodel)

        # Connection: When a subject is selected in the sidebar, update the details view.
        # This uses the 'subject' property setter in SubDetails.
        selector.subject_selected.connect(lambda s: setattr(details, 'subject', s))
        
        # Add components to the layout
        self.layout.addWidget(selector)
        self.layout.addWidget(details)

        self.setLayout(self.layout)
