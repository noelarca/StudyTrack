from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QListWidget, QListWidgetItem, QMessageBox, QSplitter
)
from PySide6.QtCore import Qt

from ui.components.task_item_widget import TaskItemWidget
from ui.components.add_task_widget import AddTaskWidget
from ui.components.task_sidebar import TaskSidebar

class TaskManager(QWidget):
    def __init__(self, viewmodel):
        super().__init__()
        self.viewmodel = viewmodel
        self.current_filter = "Tutte"
        self.setup_ui()
        
        if self.viewmodel:
            self.viewmodel.tasks_changed.connect(self.refresh_tasks)
            self.viewmodel.subjects_changed.connect(self.refresh_subjects)

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        
        # Splitter for resizability
        splitter = QSplitter(Qt.Horizontal)
        
        # --- Left Side: Subject Sidebar ---
        self.sidebar = TaskSidebar(self.viewmodel)
        self.sidebar.subject_selected.connect(self.on_subject_selected)
        
        # --- Right Side: Task Content ---
        self.content_container = QWidget()
        content_layout = QVBoxLayout(self.content_container)
        
        # 1. Add Task Section
        self.add_task_widget = AddTaskWidget(self.viewmodel, self.sidebar.current_subject, parent=self)
        content_layout.addWidget(self.add_task_widget)
        
        # 2. Header for current filter
        self.header_label = QLabel("Tutte le attività")
        self.header_label.setStyleSheet("font-weight: bold; font-size: 16px; margin-top: 10px;")
        content_layout.addWidget(self.header_label)
        
        # 3. Tasks List
        self.tasks_list = QListWidget()
        content_layout.addWidget(self.tasks_list)
        
        splitter.addWidget(self.sidebar)
        splitter.addWidget(self.content_container)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
        
        # Initial population
        self.refresh_subjects()
        self.refresh_tasks()

    def handle_add_task(self, subject, title, description, due_date, priority):
        if subject == "Tutte":
            if self.sidebar.count() > 1:
                subject = self.sidebar.item_text(1)
            else:
                raise Exception("Aggiungi prima una materia.")
        self.viewmodel.add_task(subject, title, description, due_date, priority)

    def refresh_subjects(self):
        self.current_filter = self.sidebar.refresh_subjects(self.current_filter)

    def on_subject_selected(self, subject_name):
        self.current_filter = subject_name
        if self.current_filter == "Tutte":
            self.header_label.setText("Tutte le attività")
        else:
            self.header_label.setText(f"Attività per {self.current_filter}")
        self.refresh_tasks()

    def refresh_tasks(self):
        self.tasks_list.clear()
        if not self.viewmodel:
            return
            
        if self.current_filter == "Tutte":
            tasks = self.viewmodel.get_all_tasks()
        else:
            tasks = self.viewmodel.get_tasks_by_subject(self.current_filter)
            # Normalize list for loop below: (id, subject_name, title, description, due_date, priority, is_completed)
            tasks = [(t[0], self.current_filter, t[2], t[3], t[4], t[5], t[6]) for t in tasks]

        for t in tasks:
            item = QListWidgetItem(self.tasks_list)
            display_title = f"[{t[1]}] {t[2]}" if self.current_filter == "Tutte" else t[2]
            
            widget = TaskItemWidget(
                task_id=t[0], 
                title=display_title, 
                description=t[3], 
                due_date=t[4], 
                priority=t[5], 
                is_completed=t[6], 
                viewmodel=self.viewmodel
            )
            item.setSizeHint(widget.sizeHint())
            self.tasks_list.addItem(item)
            self.tasks_list.setItemWidget(item, widget)
