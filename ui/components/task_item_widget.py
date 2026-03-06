from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QPushButton, QMessageBox
from PySide6.QtCore import Qt

class TaskItemWidget(QWidget):
    def __init__(self, task_id, title, description, due_date, priority, is_completed, viewmodel, parent=None):
        super().__init__(parent)
        self.task_id = task_id
        self.viewmodel = viewmodel
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Top Row: Checkbox, Title, Priority, Delete
        top_layout = QHBoxLayout()
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(bool(is_completed))
        self.checkbox.stateChanged.connect(self.on_toggle)
        
        self.label = QLabel(title)
        self.label.setStyleSheet("font-weight: bold;")
        if is_completed:
            self.label.setStyleSheet("text-decoration: line-through; color: gray; font-weight: bold;")
            
        priority_map = {1: "Bassa", 2: "Media", 3: "Alta"}
        priority_colors = {1: "green", 2: "#e67e22", 3: "red"}
        self.priority_label = QLabel(f"Prio: {priority_map.get(priority, 'N/A')}")
        self.priority_label.setStyleSheet(f"color: {priority_colors.get(priority, 'black')}; font-size: 10px;")
        
        self.delete_btn = QPushButton("Elimina")
        self.delete_btn.setFixedWidth(60)
        self.delete_btn.clicked.connect(self.on_delete)
        
        top_layout.addWidget(self.checkbox)
        top_layout.addWidget(self.label, 1)
        top_layout.addWidget(self.priority_label)
        top_layout.addWidget(self.delete_btn)
        main_layout.addLayout(top_layout)
        
        # Bottom Row: Description and Due Date
        if description or due_date:
            info_layout = QHBoxLayout()
            info_layout.setContentsMargins(30, 0, 0, 0)
            
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
        is_completed = (state == Qt.Checked.value)
        try:
            self.viewmodel.toggle_task_completion(self.task_id, is_completed)
            if is_completed:
                self.label.setStyleSheet("text-decoration: line-through; color: gray; font-weight: bold;")
            else:
                self.label.setStyleSheet("font-weight: bold;")
        except Exception as e:
            QMessageBox.critical(self, "Errore", str(e))

    def on_delete(self):
        try:
            self.viewmodel.delete_task(self.task_id)
        except Exception as e:
            QMessageBox.critical(self, "Errore", str(e))
