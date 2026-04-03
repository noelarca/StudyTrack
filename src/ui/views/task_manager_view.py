from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QListWidget, QListWidgetItem, QMessageBox, QSplitter
)
from PySide6.QtCore import Qt

from ui.components.task.task_item_widget import TaskItemWidget
from ui.components.task.add_task_widget import AddTaskWidget
from ui.components.task.task_sidebar import TaskSidebar

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
            # Use granular signals for better performance with many tasks
            self.viewmodel.task_added.connect(self.on_task_added, Qt.QueuedConnection)
            self.viewmodel.task_updated.connect(self.on_task_updated, Qt.QueuedConnection)
            self.viewmodel.task_deleted.connect(self.on_task_deleted, Qt.QueuedConnection)
            self.viewmodel.subjects_changed.connect(self.refresh_subjects, Qt.QueuedConnection)

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

    def refresh_subjects(self):
        """Refreshes the sidebar and add task widget subject list."""
        self.current_filter = self.sidebar.refresh_subjects(self.current_filter)
        self.add_task_widget.refresh_subjects()

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
            self.add_task_widget.set_current_subject(subject_name)
        self.refresh_tasks()

    def refresh_tasks(self):
        """
        Clears and repopulates the task list based on the current filter.
        Fetches tasks from the viewmodel and wraps them in TaskItemWidgets.
        """
        if not self.viewmodel:
            return

        # Disable updates to prevent flicker and improve performance when adding many items
        self.tasks_list.setUpdatesEnabled(False)
        try:
            self.tasks_list.clear()
            
            # Fetch filtered tasks
            if self.current_filter == "Tutte":
                tasks = self.viewmodel.get_all_tasks()
                # If we have too many tasks, show only a subset for performance
                # and maybe add a message or "load more" (omitted for brevity)
                if len(tasks) > 200:
                    self.header_label.setText(f"Tutte le attività (mostrate prime 200 di {len(tasks)})")
                    tasks = tasks[:200]
            else:
                tasks = self.viewmodel.get_tasks_by_subject(self.current_filter)
                # Normalize list for uniform processing: (id, subject_name, title, description, due_date, priority, is_completed)
                tasks = [(t[0], self.current_filter, t[2], t[3], t[4], t[5], t[6]) for t in tasks]

            # Add each task to the list widget
            for t in tasks:
                self._add_task_item(t)
        finally:
            self.tasks_list.setUpdatesEnabled(True)

    def _add_task_item(self, t):
        """Helper to create and add a single task item to the list."""
        item = QListWidgetItem(self.tasks_list)
        # Store task_id in UserRole for later lookup
        item.setData(Qt.UserRole, t[0])
        
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

    def _find_item_by_task_id(self, task_id):
        """Finds the QListWidgetItem associated with a given task_id."""
        for i in range(self.tasks_list.count()):
            item = self.tasks_list.item(i)
            if item.data(Qt.UserRole) == task_id:
                return item, i
        return None, -1

    def on_task_added(self, task_id):
        """Incremental update for a new task."""
        # Only add if it matches the current filter
        task = self.viewmodel.get_task_by_id(task_id)
        if task:
            if self.current_filter == "Tutte" or task[1] == self.current_filter:
                self._add_task_item(task)

    def on_task_updated(self, task_id):
        """Incremental update for an edited task."""
        item, index = self._find_item_by_task_id(task_id)
        if item:
            task = self.viewmodel.get_task_by_id(task_id)
            if task:
                # If it still matches filter, update it
                if self.current_filter == "Tutte" or task[1] == self.current_filter:
                    display_title = f"[{task[1]}] {task[2]}" if self.current_filter == "Tutte" else task[2]
                    widget = TaskItemWidget(
                        task_id=task[0], 
                        title=display_title, 
                        description=task[3], 
                        due_date=task[4], 
                        priority=task[5], 
                        is_completed=task[6], 
                        viewmodel=self.viewmodel
                    )
                    item.setSizeHint(widget.sizeHint())
                    self.tasks_list.setItemWidget(item, widget)
                else:
                    # No longer matches filter, remove it
                    self.tasks_list.takeItem(index)

    def on_task_deleted(self, task_id):
        """Incremental update for a deleted task."""
        item, index = self._find_item_by_task_id(task_id)
        if index != -1:
            self.tasks_list.takeItem(index)
