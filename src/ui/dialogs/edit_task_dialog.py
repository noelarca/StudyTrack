from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QDateEdit, QComboBox, QMessageBox
)
from PySide6.QtCore import Qt, QDate
from datetime import date

class EditTaskDialog(QDialog):
    """
    A dialog for editing existing tasks.
    Pre-populates fields with current task data and updates via the viewmodel.
    """
    def __init__(self, task_data, viewmodel, parent=None):
        """
        Initializes the edit task dialog.
        
        Args:
            task_data (tuple): (id, subject_name, title, description, due_date, priority, is_completed)
            viewmodel (ViewModel): The business logic controller.
        """
        super().__init__(parent)
        self.task_id = task_data[0]
        self.subject_name = task_data[1]
        self.viewmodel = viewmodel
        
        self.setWindowTitle("Modifica Attività")
        self.setMinimumWidth(400)
        self.setup_ui(task_data)

    def setup_ui(self, data):
        """Initializes the UI layout and widgets with task data."""
        layout = QVBoxLayout(self)
        
        # Row 1: Subject (Read-only for now, or editable if needed)
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Materia:"))
        self.subject_combo = QComboBox()
        self.populate_subjects()
        index = self.subject_combo.findText(data[1])
        if index >= 0:
            self.subject_combo.setCurrentIndex(index)
        row1.addWidget(self.subject_combo, 1)
        layout.addLayout(row1)
        
        # Row 2: Title
        layout.addWidget(QLabel("Titolo:"))
        self.title_input = QLineEdit()
        self.title_input.setText(data[2])
        layout.addWidget(self.title_input)
        
        # Row 3: Description
        layout.addWidget(QLabel("Descrizione:"))
        self.desc_input = QLineEdit()
        self.desc_input.setText(data[3] or "")
        layout.addWidget(self.desc_input)
        
        # Row 4: Due Date and Priority
        row4 = QHBoxLayout()
        row4.addWidget(QLabel("Scadenza:"))
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        if data[4]: # due_date is string "YYYY-MM-DD"
            self.date_input.setDate(QDate.fromString(data[4], "yyyy-MM-dd"))
        else:
            self.date_input.setDate(QDate.currentDate())
        row4.addWidget(self.date_input)
        
        row4.addWidget(QLabel("Priorità:"))
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Bassa", "Media", "Alta"])
        self.priority_combo.setCurrentIndex(data[5] - 1) # 1-3 to 0-2
        row4.addWidget(self.priority_combo)
        layout.addLayout(row4)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Salva Modifiche")
        self.save_btn.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold;")
        self.save_btn.clicked.connect(self.save_changes)
        
        self.cancel_btn = QPushButton("Annulla")
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)
        layout.addLayout(btn_layout)

    def populate_subjects(self):
        """Populates the subject combo box from the viewmodel."""
        if self.viewmodel:
            subjects = self.viewmodel.get_subjects()
            for s in subjects:
                self.subject_combo.addItem(s[1])

    def save_changes(self):
        """Validates input and updates the task via the viewmodel."""
        subject = self.subject_combo.currentText()
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Attenzione", "Il titolo non può essere vuoto.")
            return
            
        description = self.desc_input.text().strip()
        due_date = self.date_input.date().toString("yyyy-MM-dd")
        priority = self.priority_combo.currentIndex() + 1
        
        try:
            self.viewmodel.update_task(
                self.task_id, 
                subject, 
                title, 
                description, 
                due_date, 
                priority
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile aggiornare il task: {str(e)}")
