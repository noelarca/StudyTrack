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
        
        # Row 1: Subject selection and Title input
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Materia:"))
        self.subject_combo = QComboBox()
        row1.addWidget(self.subject_combo, 1)
        
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Titolo attività...")
        row1.addWidget(self.task_input, 2)
        
        self.add_btn = QPushButton("Aggiungi")
        self.add_btn.clicked.connect(self.add_task)
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
        
        # Initial population
        self.refresh_subjects()

    def refresh_subjects(self):
        """Updates the subject list in the combo box."""
        self.subject_combo.clear()
        if self.viewmodel:
            subjects = self.viewmodel.get_subjects()
            for s in subjects:
                # s is (id, name, credits)
                self.subject_combo.addItem(s[1])
        
        # Try to sync with current selection from sidebar
        current = self.current_subject_getter()
        if current and current != "Tutte":
            self.set_current_subject(current)

    def set_current_subject(self, subject_name):
        """Sets the current subject in the combo box."""
        index = self.subject_combo.findText(subject_name)
        if index >= 0:
            self.subject_combo.setCurrentIndex(index)

    def add_task(self):
        """Validates input and creates a new task through the viewmodel."""
        subject = self.subject_combo.currentText()
        if not subject:
            QMessageBox.warning(self, "Attenzione", "Seleziona una materia prima di aggiungere un'attività.")
            return
        
        title = self.task_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Attenzione", "Inserisci un titolo per l'attività.")
            return
            
        description = self.desc_input.text().strip()
        due_date = self.date_input.date().toString("yyyy-MM-dd")
        priority = self.priority_combo.currentIndex() + 1 # 1: Low, 2: Med, 3: High
            
        try:
            self.viewmodel.add_task(subject, title, description, due_date, priority)
            
            # Reset form on success
            self.task_input.clear()
            self.desc_input.clear()
            self.date_input.setDate(QDate.currentDate())
            self.priority_combo.setCurrentIndex(1)
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile aggiungere il task: {str(e)}")
