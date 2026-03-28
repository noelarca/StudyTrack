from datetime import date
from PySide6.QtCore import Signal
from core.viewmodels.base_viewmodel import BaseViewModel
from core.models import Task

class TaskViewModel(BaseViewModel):
    """
    Handles all logic related to task management.
    """
    tasks_changed = Signal()

    def __init__(self, repository):
        super().__init__(repository)

    def add_task(self, subject_name, title, description="", due_date_str=None, priority=2):
        if not title:
            raise ValueError("Task title cannot be empty.")
        
        subject_id = self.repository.get_subject_id_by_name(subject_name)
        if not subject_id:
            raise ValueError("Subject does not exist.")

        try:
            # Convert string to Value Object
            due_date = date.fromisoformat(due_date_str) if due_date_str else None
            
            task = Task(
                id=None, 
                subject_id=subject_id, 
                title=title, 
                description=description,
                due_date=due_date,
                priority=priority
            )
            self.repository.add_task(task)
            self.tasks_changed.emit()
        except Exception as e:
            raise ValueError(f"An error occurred while adding the task: {e}")

    def get_tasks_by_subject(self, subject_name):
        subject_id = self.repository.get_subject_id_by_name(subject_name)
        if not subject_id:
            return []
        try:
            return self.repository.get_tasks_by_subject(subject_id)
        except Exception as e:
            raise ValueError(f"An error occurred while fetching tasks: {e}")

    def get_all_tasks(self):
        try:
            return self.repository.get_all_tasks()
        except Exception as e:
            raise ValueError(f"An error occurred while fetching all tasks: {e}")

    def toggle_task_completion(self, task_id, is_completed):
        try:
            self.repository.update_task_status(task_id, is_completed)
            self.tasks_changed.emit()
        except Exception as e:
            raise ValueError(f"An error occurred while updating task: {e}")

    def delete_task(self, task_id):
        try:
            self.repository.delete_task(task_id)
            self.tasks_changed.emit()
        except Exception as e:
            raise ValueError(f"An error occurred while deleting task: {e}")

    def update_task(self, task_id, subject_name, title, description="", due_date_str=None, priority=2):
        try:
            subject_id = self.repository.get_subject_id_by_name(subject_name)
            if subject_id is None:
                raise ValueError("Subject does not exist.")
            if not title:
                raise ValueError("Task title cannot be empty.")
                
            due_date = date.fromisoformat(due_date_str) if due_date_str else None
            
            self.repository.update_task(task_id, subject_id, title, description, due_date, priority)
            self.tasks_changed.emit()
        except Exception as e:
            raise ValueError(f"An error occurred while updating task: {e}")

    def get_task_by_id(self, task_id):
        try:
            return self.repository.get_task_by_id(task_id)
        except Exception as e:
            raise ValueError(f"An error occurred while fetching task: {e}")
