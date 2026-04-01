from datetime import date, datetime
from core.database import Database
from core.models import Subject, StudySession, Task
from core.repositories.subject_repository import SubjectRepository
from core.repositories.session_repository import SessionRepository
from core.repositories.task_repository import TaskRepository

class StudyRepository:
    """
    Facade Repository that delegates to specialized repositories.
    This maintains backward compatibility with the ViewModel while 
    organizing code into domain-specific files.
    """
    def __init__(self, database: Database):
        self.database = database
        self.subjects = SubjectRepository(database)
        self.sessions = SessionRepository(database)
        self.tasks = TaskRepository(database)

    # --- Subject Methods ---
    def add_subject(self, subject: Subject) -> int:
        return self.subjects.add_subject(subject)
    
    def get_subject_id_by_name(self, name: str) -> int | None:
        return self.subjects.get_subject_id_by_name(name)
    
    def get_all_subjects(self):
        return self.subjects.get_all_subjects()
    
    def get_subject_details(self, name: str):
        return self.subjects.get_subject_details(name)
    
    def modify_subject(self, subject_id: int, name: str, semester: int, year: int, credits: int, notes: str):
        self.subjects.modify_subject(subject_id, name, semester, year, credits, notes)

    def delete_subject(self, subject_id: int):
        self.subjects.delete_subject(subject_id)

    def get_subject_quality_distribution(self, name: str):
        return self.subjects.get_subject_quality_distribution(name)

    def get_subject_stats_over_time(self, name: str, days=7):
        return self.subjects.get_subject_stats_over_time(name, days)

    def get_subject_streak(self, name: str):
        return self.subjects.get_subject_streak(name)

    # --- Session Methods ---
    def add_entry(self, entry: StudySession) -> int:
        return self.sessions.add_entry(entry)

    def get_last_entries(self, limit=10):
        return self.sessions.get_last_entries(limit)

    def delete_entry(self, entry_id: int):
        self.sessions.delete_entry(entry_id)

    def get_entry_by_id(self, entry_id: int) -> StudySession | None:
        return self.sessions.get_entry_by_id(entry_id)
    
    def modify_entry(self, entry_id: int, subject_id: int, entry_date: date, start_time: datetime, end_time: datetime, notes: str, quality: int):
        self.sessions.modify_entry(entry_id, subject_id, entry_date, start_time, end_time, notes, quality)

    def get_entries_by_date(self, date_str: str):
        return self.sessions.get_entries_by_date(date_str)
    
    def get_daily_stats(self, days=365):
        return self.sessions.get_daily_stats(days)

    # --- Task Methods ---
    def add_task(self, task: Task) -> int:
        return self.tasks.add_task(task)

    def get_tasks_by_subject(self, subject_id: int):
        return self.tasks.get_tasks_by_subject(subject_id)

    def get_all_tasks(self):
        return self.tasks.get_all_tasks()

    def update_task_status(self, task_id: int, is_completed: bool):
        self.tasks.update_task_status(task_id, is_completed)

    def update_task(self, task_id: int, subject_id: int, title: str, description: str, due_date: date, priority: int):
        self.tasks.update_task(task_id, subject_id, title, description, due_date, priority)

    def get_task_by_id(self, task_id: int):
        return self.tasks.get_task_by_id(task_id)

    def delete_task(self, task_id: int):
        self.tasks.delete_task(task_id)
