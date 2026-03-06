from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QFrame, QDateEdit, QComboBox, QMessageBox
)
from PySide6.QtCore import Qt, QDate

class AddTaskWidget(QWidget):
    def __init__(self, viewmodel, current_subject_getter, parent=None):
        super().__init__(parent)
        self.viewmodel = viewmodel
        self.current_subject_getter = current_subject_getter
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        add_frame = QFrame()
        add_frame.setFrameShape(QFrame.StyledPanel)
        add_layout = QVBoxLayout(add_frame)
        
        title_label = QLabel("Aggiungi Nuova Attività")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        add_layout.addWidget(title_label)
        
        # Row 1: Title and Add button
        row1 = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Titolo attività...")
        self.add_btn = QPushButton("Aggiungi")
        self.add_btn.clicked.connect(self.add_task)
        row1.addWidget(self.task_input, 1)
        row1.addWidget(self.add_btn)
        add_layout.addLayout(row1)
        
        # Row 2: Description
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Descrizione (opzionale)...")
        add_layout.addWidget(self.desc_input)
        
        # Row 3: Due Date and Priority
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Scadenza:"))
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        
        row3.addWidget(self.date_input)
        row3.addWidget(QLabel("Priorità:"))
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Bassa", "Media", "Alta"])
        self.priority_combo.setCurrentIndex(1) # Media
        row3.addWidget(self.priority_combo)
        add_layout.addLayout(row3)
        
        layout.addWidget(add_frame)

    def add_task(self):
        subject = self.current_subject_getter()
        if subject == "Tutte":
            # This logic might need to be passed in or handled by TaskManager
            # For now, let's just use what's passed
            pass

        title = self.task_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Attenzione", "Inserisci un titolo per l'attività.")
            return
            
        description = self.desc_input.text().strip()
        due_date = self.date_input.date().toString("yyyy-MM-dd")
        priority = self.priority_combo.currentIndex() + 1 # 1: Low, 2: Med, 3: High
            
        try:
            # We'll let the TaskManager handle the actual addition if subject needs logic
            self.parent().handle_add_task(subject, title, description, due_date, priority)
            self.task_input.clear()
            self.desc_input.clear()
            self.date_input.setDate(QDate.currentDate())
            self.priority_combo.setCurrentIndex(1)
        except Exception as e:
            QMessageBox.critical(self, "Errore", str(e))
