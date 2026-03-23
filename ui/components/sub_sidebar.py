"""
This module contains the SubSidebar component, which provides a list of subjects
and an interface to add new subjects, typically used in the main application's sidebar.
"""

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QListWidget,
    QLabel, QListWidgetItem
)
from ui.components.new_sub_window import NewSubjectWindow

class SubSidebar(QWidget):
    """
    A sidebar widget that displays a list of subjects and an 'Add Subject' button.
    Supports multi-line text for long subject names.
    """
    
    # signal emitted when a subject is selected (passes the subject name as a string)
    subject_selected = Signal(str)

    def __init__(self, viewmodel=None):
        """
        Initializes the SubSidebar widget.
        """
        super().__init__()
        self.viewmodel = viewmodel

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)

        # Title for the sidebar section
        self.title = QLabel("MATERIE")
        self.title.setStyleSheet("color: #90a4ae; font-weight: bold; font-size: 11px; letter-spacing: 1px; margin-bottom: 5px;")

        # List widget to display subjects
        self.subject_list = QListWidget()
        self.subject_list.setWordWrap(True) # Enable word wrap
        self.subject_list.setTextElideMode(Qt.ElideNone) # Don't cut off with "..."
        
        # Style the list widget to match the modern theme
        self.subject_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                outline: none;
            }
            QListWidget::item {
                padding: 10px;
                border-radius: 8px;
                color: #eceff1;
                margin-bottom: 4px;
            }
            QListWidget::item:hover {
            }
            QListWidget::item:selected {
                font-weight: bold;
            }
        """)
        
        # Load initial subjects
        self.load_subjects()
        
        # Selection handler
        self.subject_list.itemClicked.connect(self.on_subject_clicked)
        
        # Auto-refresh
        if self.viewmodel is not None and hasattr(self.viewmodel, 'subjects_changed'):
            self.viewmodel.subjects_changed.connect(self.load_subjects, Qt.QueuedConnection)
        
        # Add Button
        self.add_button = QPushButton("+ Aggiungi Materia")
        self.add_button.setCursor(Qt.PointingHandCursor)
        self.add_button.setStyleSheet("""
            QPushButton {
                border: 2px dashed #000000;
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
            }
                
        """)
        self.add_button.clicked.connect(self.addsubject)

        # Assemble the layout
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.subject_list)
        self.layout.addWidget(self.add_button)

    def load_subjects(self):
        """
        Fetches and populates the list with multi-line support.
        """
        self.subject_list.clear()
        subjects = self.viewmodel.get_subjects()
        
        if subjects:
            for s in subjects:
                name = s[1] if isinstance(s, (tuple, list)) and len(s) > 1 else str(s)
                item = QListWidgetItem(name)
                # Ensure the item can grow in height to accommodate wrapped text
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.subject_list.addItem(item)

    def addsubject(self):
        try:
            self.SubWindow = NewSubjectWindow(viewmodel=self.viewmodel)
            self.SubWindow.show()
        except Exception as e:
            print(f"Error adding subject: {e}")

    def on_subject_clicked(self, item):
        subject = item.text()
        self.viewmodel.select_subject(subject)
        self.subject_selected.emit(subject)
