"""
This module contains the SubGrid component, which displays a grid of subjects
as selectable buttons, allowing users to interact with individual subjects.
"""

import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QButtonGroup, QGridLayout, QWidget, QPushButton


class SubGrid(QWidget):
    """
    A widget that displays subjects in a grid layout.
    
    Each subject is represented by a checkable QPushButton. Selecting a button
    can trigger actions related to that specific subject.
    """

    def __init__(self, title: str = "Materie", viewmodel=None, parent=None):
        """
        Initializes the SubGrid widget.

        Args:
            title (str): The title for the grid (default: "Materie").
            viewmodel: The ViewModel instance to handle business logic and data.
            parent: The parent widget, if any.
        """
        super().__init__(parent)
        self.viewmodel = viewmodel

        # Grid layout to arrange subject buttons
        self.layout = QGridLayout(self)

        # Button group to manage exclusive selection of subject buttons
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)  # Only one button can be checked at a time

        # Fetch initial list of subjects from the viewmodel
        if self.viewmodel is None:
            print("SubGrid: viewmodel is None, cannot load subjects")
            self.subs = []
        else:
            try:
                self.subs = self.viewmodel.get_subjects()
            except Exception as e:
                print(f"Errore durante il caricamento delle materie: {e}")
                self.subs = []

        if self.subs is None:
            self.subs = []

        # Populate the grid with buttons for the current subjects
        self._populate_buttons()

        # Connect to the viewmodel's subjects_changed signal to refresh the grid automatically
        if self.viewmodel is not None and hasattr(self.viewmodel, 'subjects_changed'):
            try:
                self.viewmodel.subjects_changed.connect(self.refresh_grid, Qt.QueuedConnection)
            except Exception:
                # Signal might not be available or connection failed
                pass

    def on_sub_clicked(self, sub):
        """
        Handles the event when a subject button is clicked.

        Args:
            sub: The subject data associated with the clicked button.
        
        Returns:
            str: The normalized subject name string.
        """
        # Normalize returned value to the subject name string
        # Handles cases where 'sub' might be a tuple/list (e.g., from database) or a string
        if isinstance(sub, (tuple, list)) and len(sub) > 1:
            return sub[1]
        return str(sub)

    def _populate_buttons(self):
        """
        Internal helper method to create and add buttons to the grid layout.
        """
        # If no subjects are available, show a disabled placeholder button
        if not self.subs:
            button = QPushButton("Nessuna materia disponibile")
            button.setEnabled(False)
            self.layout.addWidget(button)
            self.button_group.addButton(button)
            return

        # Create a button for each subject and add it to the layout
        for sub in self.subs:
            if isinstance(sub, (tuple, list)) and len(sub) > 1:
                name = sub[1]
            else:
                name = str(sub)
            
            button = QPushButton(name)
            # Use a lambda with a default argument to capture the current subject 'sub'
            button.clicked.connect(lambda checked, s=sub: self.on_sub_clicked(s))
            button.setCheckable(True)
            button.setMinimumHeight(20)
            button.setMaximumWidth(100)
            
            self.layout.addWidget(button)
            self.button_group.addButton(button)

    def refresh_grid(self):
        """
        Clears the current grid and reloads subjects from the viewmodel.
        This is typically called in response to data changes in the viewmodel.
        """
        # Remove all existing widgets from the layout and clean them up
        while self.layout.count():
            item = self.layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)

        # Reload the latest subjects from the viewmodel
        try:
            self.subs = self.viewmodel.get_subjects() or []
        except Exception:
            self.subs = []
            
        # Re-populate the grid with the updated subject list
        self._populate_buttons()
