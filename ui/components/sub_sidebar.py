"""
This module contains the SubSidebar component, which provides a list of subjects
and an interface to add new subjects, typically used in the main application's sidebar.
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QListWidget,
    QLabel
)
from ui.components.new_sub_window import NewSubjectWindow

class SubSidebar(QWidget):
    """
    A sidebar widget that displays a list of subjects and an 'Add Subject' button.
    
    It emits a signal when a subject is selected from the list, allowing other 
    components to respond to the selection.
    """
    
    # signal emitted when a subject is selected (passes the subject name as a string)
    subject_selected = Signal(str)

    def __init__(self, viewmodel=None):
        """
        Initializes the SubSidebar widget.

        Args:
            viewmodel: The ViewModel instance to handle business logic and data.
        """
        super().__init__()
        self.viewmodel = viewmodel

        self.layout = QVBoxLayout(self)

        # Title for the sidebar section
        self.title = QLabel("Materie:")

        # List widget to display subjects
        self.subject_list = QListWidget()
        
        # Load initial subjects into the list widget
        self.load_subjects()
        
        # Connect clicking an item in the list to the selection handler
        self.subject_list.itemClicked.connect(lambda item: self.on_subject_clicked(item))
        
        # Auto-refresh the list whenever the subjects list in the viewmodel changes
        if self.viewmodel is not None and hasattr(self.viewmodel, 'subjects_changed'):
            try:
                self.viewmodel.subjects_changed.connect(self.load_subjects)
            except Exception:
                # Signal connection failed or signal does not exist
                pass
        
        # Button to open the window for adding a new subject
        self.add_button = QPushButton("Aggiungi materia")
        self.add_button.clicked.connect(self.addsubject)

        # Assemble the layout
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.subject_list)
        self.layout.addWidget(self.add_button)

    def load_subjects(self):
        """
        Fetches the latest subjects from the viewmodel and populates the list widget.
        """
        # Clear the current list before reloading
        self.subject_list.clear()
        
        # Retrieve the latest subjects from the viewmodel
        subjects = self.viewmodel.get_subjects()
        
        if subjects is not None:
            # Normalize returned subjects into strings for display in the list widget
            if isinstance(subjects, str):
                # Ensure subjects is a list if it's a single string
                subjects = [subjects]
            else:
                # Handle database-style results (tuples/lists) by extracting the name field (index 1)
                subjects = [
                    s[1] if isinstance(s, (tuple, list)) and len(s) > 1 else str(s)
                    for s in subjects
                ]
            
            # Add all processed subject names to the list widget
            self.subject_list.addItems(subjects)

    def addsubject(self):
        """
        Opens the 'New Subject' window to allow the user to create a new subject.
        """
        try:
            # Create and show the new subject window, passing the current viewmodel
            self.SubWindow = NewSubjectWindow(viewmodel=self.viewmodel)
            self.SubWindow.show()
            # The UI will automatically refresh when the new subject is saved 
            # and the `subjects_changed` signal is emitted.
        except Exception as e:
            print(f"Error adding subject: {e}")

    def on_subject_clicked(self, item):
        """
        Handles the event when a subject is clicked in the list widget.

        Args:
            item (QListWidgetItem): The item representing the selected subject.
        """
        subject = item.text()
        
        # Update the selected subject in the viewmodel to reflect the choice globally
        self.viewmodel.select_subject(subject)
        
        # Notify any connected listeners about the new subject selection
        self.subject_selected.emit(subject)
