from database import Database, Subject, StudySession, Task

class StudyRepository:
    def __init__(self, database: Database):
        self.database = database

    def add_entry(self, entry: StudySession) -> int:
        return self.database.add_entry(entry)

    def add_subject(self, subject: Subject) -> int:
        return self.database.add_subject(subject)
    
    def get_subject_id_by_name(self, name: str) -> int | None:
        return self.database.get_subject_id_by_name(name)
    
    def get_all_subjects(self):
        # returns list of tuples (id, name, credits)
        return self.database.get_all_subjects()
    
    def get_last_entries(self, limit=10):
        return self.database.get_last_entries(limit)

    def get_subject_details(self, name: str):
        details = self.database.get_subject_by_name(name) + self.database.get_subject_minor_stats(name)
        return details
    
    def modify_subject(self, subject_id: int, name: str, semester: int, year: int, credits: int, notes: str):
        self.database.modify_subject(subject_id, name, semester, year, credits, notes)

    def delete_subject(self, subject_id: int):
        self.database.delete_subject(subject_id)

    def delete_entry(self, entry_id: int):
        self.database.delete_entry(entry_id)

    def get_entry_by_id(self, entry_id: int) -> tuple:
        return self.database.get_entry_by_id(entry_id)
    
    def modify_entry(self, entry_id: int, subject: str, date: str, start_time: str, end_time: str, notes: str, quality: int):
        subject_id = self.get_subject_id_by_name(subject)
        if subject_id is None:
            raise ValueError("Subject does not exist.")
        self.database.modify_entry(entry_id, subject_id, date, start_time, end_time, notes, quality)

    def get_subject_stats_over_time(self, name: str, days=7):
        return self.database.get_subject_stats_over_time(name, days)

    def get_entries_by_date(self, date_str: str):
        return self.database.get_entries_by_date(date_str)

    # --- TASK METHODS ---
    def add_task(self, task: Task) -> int:
        return self.database.add_task(task)

    def get_tasks_by_subject(self, subject_id: int):
        return self.database.get_tasks_by_subject(subject_id)

    def get_all_tasks(self):
        return self.database.get_all_tasks()

    def update_task_status(self, task_id: int, is_completed: bool):
        self.database.update_task_status(task_id, is_completed)

    def delete_task(self, task_id: int):
        self.database.delete_task(task_id)