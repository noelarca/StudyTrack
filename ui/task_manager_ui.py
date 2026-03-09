from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QListWidget, QListWidgetItem, QMessageBox, QSplitter
)
from PySide6.QtCore import Qt

from ui.components.task_item_widget import TaskItemWidget
from ui.components.add_task_widget import AddTaskWidget
from ui.components.task_sidebar import TaskSidebar

class TaskManager(QWidget):
    """
    UI component for managing tasks across different subjects.
    Provides a sidebar to filter tasks by subject and a main area to 
    add, view, and complete tasks.
    """
    def __init__(self, viewmodel):
        """
        Initializes the task manager.
        
        Args:
            viewmodel (ViewModel): The viewmodel for data binding and operations.
        """
        super().__init__()
        self.viewmodel = viewmodel
        self.current_filter = "Tutte"  # Default filter: show all tasks
        self.setup_ui()
        
        # Connect to viewmodel signals to auto-refresh when data changes
        if self.viewmodel:
            self.viewmodel.tasks_changed.connect(self.refresh_tasks)
            self.viewmodel.subjects_changed.connect(self.refresh_subjects)

    def setup_ui(self):
        """Sets up the layout, sidebar, and task list."""
        main_layout = QHBoxLayout(self)
        
        # Splitter allows users to resize the sidebar/content area
        splitter = QSplitter(Qt.Horizontal)
        
        # --- LEFT SIDE: SUBJECT SIDEBAR ---
        self.sidebar = TaskSidebar(self.viewmodel)
        self.sidebar.subject_selected.connect(self.on_subject_selected)
        
        # --- RIGHT SIDE: TASK CONTENT ---
        self.content_container = QWidget()
        content_layout = QVBoxLayout(self.content_container)
        
        # 1. Add Task Section (Form to create new tasks)
        self.add_task_widget = AddTaskWidget(self.viewmodel, self.sidebar.current_subject, parent=self)
        self.add_task_widget.task_added.connect(self.handle_add_task)
        content_layout.addWidget(self.add_task_widget)
        
        # 2. Header for current filter (e.g., "Tasks for Physics")
        self.header_label = QLabel("Tutte le attività")
        self.header_label.setStyleSheet("font-weight: bold; font-size: 16px; margin-top: 10px;")
        content_layout.addWidget(self.header_label)
        
        # 3. Tasks List (Scrollable list of TaskItemWidgets)
        self.tasks_list = QListWidget()
        content_layout.addWidget(self.tasks_list)
        
        # Assemble splitter
        splitter.addWidget(self.sidebar)
        splitter.addWidget(self.content_container)
        splitter.setStretchFactor(1, 1) # Content area expands more than sidebar
        
        main_layout.addWidget(splitter)
        
        # Initial population of data
        self.refresh_subjects()
        self.refresh_tasks()

    def handle_add_task(self, subject, title, description, due_date, priority):
        """
        Handles the logic for adding a new task, ensuring a subject is selected.
        
        Args:
            subject (str): Selected subject name.
            title (str): Task title.
            description (str): Task description.
            due_date (str): Due date.
            priority (int): Priority level.
        """
        if subject == "Tutte":
            # If "All" is selected, try to pick the first available subject
            if self.sidebar.count() > 1:
                subject = self.sidebar.item_text(1)
            else:
                raise Exception("Aggiungi prima una materia.")
        self.viewmodel.add_task(subject, title, description, due_date, priority)

    def refresh_subjects(self):
        """Refreshes the sidebar subject list."""
        self.current_filter = self.sidebar.refresh_subjects(self.current_filter)

    def on_subject_selected(self, subject_name):
        """
        Callback when a subject is selected in the sidebar.
        Updates the filter and refreshes the task list.
        """
        self.current_filter = subject_name
        if self.current_filter == "Tutte":
            self.header_label.setText("Tutte le attività")
        else:
            self.header_label.setText(f"Attività per {self.current_filter}")
        
        # Sync the add task widget's subject selector
        self.add_task_widget.refresh_subjects()
        
        self.refresh_tasks()

    def refresh_tasks(self):
        """
        Clears and repopulates the task list based on the current filter.
        Fetches tasks from the viewmodel and wraps them in TaskItemWidgets.
        """
        self.tasks_list.clear()
        if not self.viewmodel:
            return
            
        # Fetch filtered tasks
        if self.current_filter == "Tutte":
            tasks = self.viewmodel.get_all_tasks()
        else:
            tasks = self.viewmodel.get_tasks_by_subject(self.current_filter)
            # Normalize list for uniform processing: (id, subject_name, title, description, due_date, priority, is_completed)
            tasks = [(t[0], self.current_filter, t[2], t[3], t[4], t[5], t[6]) for t in tasks]

        # Add each task to the list widget
        for t in tasks:
            item = QListWidgetItem(self.tasks_list)
            # Include subject name in title if viewing "All tasks"
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
