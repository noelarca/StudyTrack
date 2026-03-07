# ui/components/task_sidebar.py
"""
Sidebar widget for filtering tasks by subject.
Provides a list of available subjects and emits signals when selection changes.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget
from PySide6.QtCore import Signal

class TaskSidebar(QWidget):
    """
    A sidebar widget that allows users to filter tasks by selecting a subject.
    
    Signals:
        subject_selected (str): Emitted when a subject in the list is clicked.
    """
    subject_selected = Signal(str)

    def __init__(self, viewmodel, parent=None):
        super().__init__(parent)
        self.viewmodel = viewmodel
        self.setup_ui()

    def setup_ui(self):
        """Initializes the UI components of the sidebar."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 5, 0)
        
        sidebar_label = QLabel("Filtra Materie:")
        sidebar_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(sidebar_label)
        
        self.subject_list = QListWidget()
        self.subject_list.setFixedWidth(180)
        self.subject_list.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.subject_list)

    def on_item_clicked(self, item):
        """Handles the click event on a subject item."""
        self.subject_selected.emit(item.text())

    def refresh_subjects(self, current_filter):
        """
        Reloads the subject list from the viewmodel.
        
        Args:
            current_filter (str): The name of the subject currently being filtered.
            
        Returns:
            str: The actual current filter name (fallback to 'Tutte' if not found).
        """
        self.subject_list.clear()
        self.subject_list.addItem("Tutte")
        
        subjects = self.viewmodel.get_subjects() if self.viewmodel else []
        for s in subjects:
            # Assumes subject is a tuple (id, name, ...) or similar
            name = s[1] if isinstance(s, (tuple, list)) else str(s)
            self.subject_list.addItem(name)
            
        # Try to restore previous selection
        found = False
        for i in range(self.subject_list.count()):
            if self.subject_list.item(i).text() == current_filter:
                self.subject_list.setCurrentRow(i)
                found = True
                break
        if not found:
            self.subject_list.setCurrentRow(0)
            return "Tutte"
        return current_filter

    def current_subject(self):
        """Returns the text of the currently selected subject."""
        item = self.subject_list.currentItem()
        return item.text() if item else "Tutte"

    def count(self):
        """Returns the number of items in the subject list."""
        return self.subject_list.count()

    def item_text(self, index):
        """Returns the text of the item at the specified index."""
        return self.subject_list.item(index).text()
