from PySide6.QtCore import QObject, Signal
from core.viewmodels.subject_viewmodel import SubjectViewModel
from core.viewmodels.session_viewmodel import SessionViewModel
from core.viewmodels.task_viewmodel import TaskViewModel

class ViewModel(QObject):
    """
    The main ViewModel acts as a facade, delegating specific logic to 
    specialized sub-viewmodels while maintaining backward compatibility with the UI.
    """
    # Expose signals from sub-viewmodels at the top level
    subjects_changed = Signal()
    entries_changed = Signal()
    tasks_changed = Signal()
    task_added = Signal(int)
    task_updated = Signal(int)
    task_deleted = Signal(int)
    settings_changed = Signal()

    def __init__(self, repository):
        super().__init__()
        self.repository = repository
        
        # Initialize specialized viewmodels
        self.subject_vm = SubjectViewModel(repository)
        self.session_vm = SessionViewModel(repository)
        self.task_vm = TaskViewModel(repository)

        # Forward signals from sub-viewmodels to our main signals
        self.subject_vm.subjects_changed.connect(self.subjects_changed.emit)
        self.session_vm.entries_changed.connect(self.entries_changed.emit)
        self.task_vm.tasks_changed.connect(self.tasks_changed.emit)
        self.task_vm.task_added.connect(self.task_added.emit)
        self.task_vm.task_updated.connect(self.task_updated.emit)
        self.task_vm.task_deleted.connect(self.task_deleted.emit)
        
        # Base settings signals
        self.subject_vm.settings_changed.connect(self.settings_changed.emit)
        self.session_vm.settings_changed.connect(self.settings_changed.emit)
        self.task_vm.settings_changed.connect(self.settings_changed.emit)

    # --- Settings (delegated to any sub-vm or kept here) ---
    def get_setting(self, key):
        return self.subject_vm.get_setting(key)

    def set_setting(self, key, value):
        self.subject_vm.set_setting(key, value)

    # --- Subject Methods ---
    def add_subject(self, *args, **kwargs):
        self.subject_vm.add_subject(*args, **kwargs)

    def get_subjects(self):
        return self.subject_vm.get_subjects()

    def get_subject_details(self, subject):
        return self.subject_vm.get_subject_details(subject)

    def update_subject(self, *args, **kwargs):
        self.subject_vm.update_subject(*args, **kwargs)

    def delete_subject(self, subject_id):
        self.subject_vm.delete_subject(subject_id)

    def get_subject_id_by_name(self, name):
        return self.subject_vm.get_subject_id_by_name(name)

    def select_subject(self, subject):
        self.selected_subject = subject

    def get_subject_quality_distribution(self, name):
        return self.subject_vm.get_subject_quality_distribution(name)

    def get_subject_stats_over_time(self, name, days=7):
        return self.subject_vm.get_subject_stats_over_time(name, days)

    def get_subject_streak(self, name):
        return self.subject_vm.get_subject_streak(name)

    def get_subject_progress(self, name):
        return self.subject_vm.get_subject_progress(name)

    # --- Session Methods ---
    def add_entry(self, *args, **kwargs):
        self.session_vm.add_entry(*args, **kwargs)

    def get_last_entries(self, limit=10):
        return self.session_vm.get_last_entries(limit)

    def delete_entry(self, entry_id):
        self.session_vm.delete_entry(entry_id)

    def get_entry_by_id(self, entry_id):
        return self.session_vm.get_entry_by_id(entry_id)

    def modify_entry(self, *args, **kwargs):
        self.session_vm.modify_entry(*args, **kwargs)

    def get_daily_stats(self, days=365):
        return self.session_vm.get_daily_stats(days)

    def get_entries_by_date(self, date_str):
        return self.session_vm.get_entries_by_date(date_str)

    # --- Task Methods ---
    def add_task(self, *args, **kwargs):
        self.task_vm.add_task(*args, **kwargs)

    def get_tasks_by_subject(self, subject_name):
        return self.task_vm.get_tasks_by_subject(subject_name)

    def get_all_tasks(self):
        return self.task_vm.get_all_tasks()

    def toggle_task_completion(self, task_id, is_completed):
        self.task_vm.toggle_task_completion(task_id, is_completed)

    def delete_task(self, task_id):
        self.task_vm.delete_task(task_id)

    def update_task(self, *args, **kwargs):
        self.task_vm.update_task(*args, **kwargs)

    def get_task_by_id(self, task_id):
        return self.task_vm.get_task_by_id(task_id)

    def get_tasks_by_date(self, date_str):
        return self.task_vm.get_tasks_by_date(date_str)
