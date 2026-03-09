# ui/components/add_task_widget.py
"""
Widget for adding new tasks to the task manager.
Includes inputs for title, description, due date, and priority level.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QFrame, QDateEdit, QComboBox, QMessageBox
)
from PySide6.QtCore import Qt, QDate, Signal

class AddTaskWidget(QWidget):
    """
    A form widget to create new tasks with specific attributes.
    
    Attributes:
        viewmodel (ViewModel): The business logic controller.
        current_subject_getter (callable): Function to get the currently selected subject filter.
        task_added (Signal): Emitted when the "Add" button is clicked and input is valid.
    """
    task_added = Signal(str, str, str, str, int)

    def __init__(self, viewmodel, current_subject_getter, parent=None):
        super().__init__(parent)
        self.viewmodel = viewmodel
        self.current_subject_getter = current_subject_getter
        self.setup_ui()
        
        # Connect to viewmodel signals to refresh subjects when they change
        if self.viewmodel:
            self.viewmodel.subjects_changed.connect(self.refresh_subjects)
        
        self.refresh_subjects()

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
        self.subject_combo.setMinimumWidth(120)
        row1.addWidget(self.subject_combo)
        
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Titolo attività...")
        row1.addWidget(self.task_input, 1)
        
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

    def refresh_subjects(self):
        """Populates the subject combo box with available subjects."""
        self.subject_combo.clear()
        subjects = self.viewmodel.get_subjects() if self.viewmodel else []
        for s in subjects:
            name = s[1] if isinstance(s, (tuple, list)) else str(s)
            self.subject_combo.addItem(name)
            
        # Try to sync with current filter
        current_filter = self.current_subject_getter()
        if current_filter != "Tutte":
            index = self.subject_combo.findText(current_filter)
            if index >= 0:
                self.subject_combo.setCurrentIndex(index)

    def add_task(self):
        """Validates input and emits the task_added signal."""
        subject = self.subject_combo.currentText()
        if not subject:
            QMessageBox.warning(self, "Attenzione", "Seleziona prima una materia. Se non ce ne sono, aggiungine una nella gestione materie.")
            return
        
        title = self.task_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Attenzione", "Inserisci un titolo per l'attività.")
            return
            
        description = self.desc_input.text().strip()
        due_date = self.date_input.date().toString("yyyy-MM-dd")
        priority = self.priority_combo.currentIndex() + 1 # 1: Low, 2: Med, 3: High
            
        try:
            # Emits the signal with task details
            self.task_added.emit(subject, title, description, due_date, priority)
            
            # Reset form on success (keep subject selection)
            self.task_input.clear()
            self.desc_input.clear()
            self.date_input.setDate(QDate.currentDate())
            self.priority_combo.setCurrentIndex(1)
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile aggiungere il task: {str(e)}")
