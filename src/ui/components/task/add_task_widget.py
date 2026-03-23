# ui/components/add_task_widget.py
"""
Widget for adding new tasks to the task manager.
Includes inputs for title, description, due date, and priority level.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QFrame, QDateEdit, QComboBox, QMessageBox
)
from PySide6.QtCore import Qt, QDate

class AddTaskWidget(QWidget):
    """
    A form widget to create new tasks with specific attributes.
    
    Attributes:
        viewmodel (ViewModel): The business logic controller.
        current_subject_getter (callable): Function to get the currently selected subject filter.
    """
    def __init__(self, viewmodel, current_subject_getter, parent=None):
        super().__init__(parent)
        self.viewmodel = viewmodel
        self.current_subject_getter = current_subject_getter
        self.setup_ui()

    def setup_ui(self):
        """Initializes the UI layout and widgets for the task entry form."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Container frame with styling
        add_frame = QFrame()
        add_frame.setFrameShape(QFrame.StyledPanel)
        add_layout = QVBoxLayout(add_frame)
        
        title_label = QLabel("Aggiungi Nuova Attività")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        add_layout.addWidget(title_label)
        
        # Row 1: Title input and Add button
        row1 = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Titolo attività...")
        self.add_btn = QPushButton("Aggiungi")
        self.add_btn.clicked.connect(self.add_task)
        row1.addWidget(self.task_input, 1)
        row1.addWidget(self.add_btn)
        add_layout.addLayout(row1)
        
        # Row 2: Optional description
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Descrizione (opzionale)...")
        add_layout.addWidget(self.desc_input)
        
        # Row 3: Metadata (Due Date and Priority level)
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Scadenza:"))
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        
        row3.addWidget(self.date_input)
        row3.addWidget(QLabel("Priorità:"))
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Bassa", "Media", "Alta"])
        self.priority_combo.setCurrentIndex(1) # Default to 'Media'
        row3.addWidget(self.priority_combo)
        add_layout.addLayout(row3)
        
        layout.addWidget(add_frame)

    def add_task(self):
        """Validates input and delegates task creation to the parent TaskManager."""
        subject = self.current_subject_getter()
        # Note: If subject is "Tutte", the parent TaskManager must handle it (e.g., prompt for subject)
        
        title = self.task_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Attenzione", "Inserisci un titolo per l'attività.")
            return
            
        description = self.desc_input.text().strip()
        due_date = self.date_input.date().toString("yyyy-MM-dd")
        priority = self.priority_combo.currentIndex() + 1 # 1: Low, 2: Med, 3: High
            
        try:
            # Calls handle_add_task on the parent widget (TaskManagerUI)
            if hasattr(self.parent(), 'handle_add_task'):
                self.parent().handle_add_task(subject, title, description, due_date, priority)
                
                # Reset form on success
                self.task_input.clear()
                self.desc_input.clear()
                self.date_input.setDate(QDate.currentDate())
                self.priority_combo.setCurrentIndex(1)
            else:
                # Fallback if parent is not as expected
                print("Error: Parent widget does not implement handle_add_task")
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile aggiungere il task: {str(e)}")
