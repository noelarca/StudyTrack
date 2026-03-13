# ui/components/task_item_widget.py
"""
Custom widget representing a single task item in a list.
Displays task details (title, description, priority, due date) and allows completion toggle and deletion.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, 
    QPushButton, QMessageBox, QDialog, QLineEdit, QDateEdit, QComboBox, QFormLayout, QTextEdit
)
from PySide6.QtCore import Qt, QDate

class EditTaskWindow(QDialog):
    """Dialog for editing an existing task."""
    def __init__(self, task_id, viewmodel, parent=None):
        super().__init__(parent)
        self.task_id = task_id
        self.viewmodel = viewmodel
        self.setWindowTitle("Modifica Attività")
        self.setMinimumWidth(400)
        self.setup_ui()
        self.load_task_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        self.subject_combo = QComboBox()
        subjects = self.viewmodel.get_subjects()
        for s in subjects:
            name = s[1] if isinstance(s, (tuple, list)) else str(s)
            self.subject_combo.addItem(name)
        form_layout.addRow("Materia:", self.subject_combo)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Inserisci il titolo dell'attività")
        self.title_input.setMinimumHeight(30)
        form_layout.addRow("Titolo:", self.title_input)

        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Inserisci una descrizione (opzionale)")
        self.desc_input.setMinimumHeight(100)
        form_layout.addRow("Descrizione:", self.desc_input)

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setMinimumHeight(30)
        form_layout.addRow("Scadenza:", self.date_input)

        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Bassa", "Media", "Alta"])
        self.priority_combo.setMinimumHeight(30)
        form_layout.addRow("Priorità:", self.priority_combo)

        layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        self.save_btn = QPushButton("Salva")
        self.save_btn.setMinimumHeight(35)
        self.save_btn.clicked.connect(self.save_task)
        self.cancel_btn = QPushButton("Annulla")
        self.cancel_btn.setMinimumHeight(35)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

    def load_task_data(self):
        try:
            task = self.viewmodel.get_task_by_id(self.task_id)
            if task:
                # task structure: (id, subject_name, title, description, due_date, priority, is_completed)
                _, subject_name, title, description, due_date, priority, _ = task
                
                index = self.subject_combo.findText(subject_name)
                if index >= 0:
                    self.subject_combo.setCurrentIndex(index)
                
                self.title_input.setText(title)
                self.desc_input.setPlainText(description or "")
                if due_date:
                    self.date_input.setDate(QDate.fromString(due_date, "yyyy-MM-dd"))
                else:
                    self.date_input.setDate(QDate.currentDate())
                
                self.priority_combo.setCurrentIndex(priority - 1)
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile caricare i dati del task: {e}")
            self.reject()

    def save_task(self):
        subject = self.subject_combo.currentText()
        title = self.title_input.text().strip()
        description = self.desc_input.toPlainText().strip()
        due_date = self.date_input.date().toString("yyyy-MM-dd")
        priority = self.priority_combo.currentIndex() + 1

        if not title:
            QMessageBox.warning(self, "Attenzione", "Il titolo non può essere vuoto.")
            return

        try:
            self.viewmodel.update_task(self.task_id, subject, title, description, due_date, priority)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile aggiornare il task: {e}")


class TaskItemWidget(QWidget):
    """
    A widget to display and manage a single task.
    
    Attributes:
        task_id (int): Unique identifier of the task.
        viewmodel (ViewModel): The business logic controller.
    """
    def __init__(self, task_id, title, description, due_date, priority, is_completed, viewmodel, parent=None):
        super().__init__(parent)
        self.task_id = task_id
        self.viewmodel = viewmodel
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Top Row: Checkbox, Title, Priority label, Edit and Delete buttons
        top_layout = QHBoxLayout()
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(bool(is_completed))
        self.checkbox.stateChanged.connect(self.on_toggle)
        
        self.label = QLabel(title)
        self.label.setStyleSheet("font-weight: bold;")
        if is_completed:
            # Visual feedback for completed tasks
            self.label.setStyleSheet("text-decoration: line-through; color: gray; font-weight: bold;")
            
        # Priority mapping and styling
        priority_map = {1: "Bassa", 2: "Media", 3: "Alta"}
        priority_colors = {1: "green", 2: "#e67e22", 3: "red"}
        self.priority_label = QLabel(f"Prio: {priority_map.get(priority, 'N/A')}")
        self.priority_label.setStyleSheet(f"color: {priority_colors.get(priority, 'black')}; font-size: 10px;")
        
        self.edit_btn = QPushButton("Modifica")
        self.edit_btn.setFixedWidth(100
                                    )
        self.edit_btn.setStyleSheet("font-size: 10px;")
        self.edit_btn.clicked.connect(self.on_edit)

        self.delete_btn = QPushButton("Elimina")
        self.delete_btn.setFixedWidth(100)
        self.delete_btn.setStyleSheet("font-size: 10px; color: #c0392b;")
        self.delete_btn.clicked.connect(self.on_delete)
        
        top_layout.addWidget(self.checkbox)
        top_layout.addWidget(self.label, 1)
        top_layout.addWidget(self.priority_label)
        top_layout.addWidget(self.edit_btn)
        top_layout.addWidget(self.delete_btn)
        main_layout.addLayout(top_layout)
        
        # Bottom Row: Optional Description and Due Date
        if description or due_date:
            info_layout = QHBoxLayout()
            info_layout.setContentsMargins(30, 0, 0, 0) # Indent from checkbox
            
            if description:
                desc_label = QLabel(description)
                desc_label.setStyleSheet("color: #555; font-style: italic; font-size: 11px;")
                desc_label.setWordWrap(True)
                info_layout.addWidget(desc_label, 1)
                
            if due_date:
                date_label = QLabel(f"Scadenza: {due_date}")
                date_label.setStyleSheet("color: #7f8c8d; font-size: 10px;")
                info_layout.addWidget(date_label)
                
            main_layout.addLayout(info_layout)

    def on_toggle(self, state):
        """Updates task completion status in the database and updates UI style."""
        is_completed = (state == Qt.Checked.value)
        try:
            self.viewmodel.toggle_task_completion(self.task_id, is_completed)
            if is_completed:
                self.label.setStyleSheet("text-decoration: line-through; color: gray; font-weight: bold;")
            else:
                self.label.setStyleSheet("font-weight: bold;")
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile aggiornare il task: {str(e)}")

    def on_edit(self):
        """Opens the edit task dialog."""
        dialog = EditTaskWindow(self.task_id, self.viewmodel, self)
        dialog.exec()

    def on_delete(self):
        """Deletes the task after user clicks the delete button."""
        confirm = QMessageBox.question(self, "Conferma", "Sei sicuro di voler eliminare questa attività?", 
                                     QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                self.viewmodel.delete_task(self.task_id)
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Impossibile eliminare il task: {str(e)}")
