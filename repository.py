from database import Database, Subject, StudySession

class StudyRepository:
    def __init__(self, database: Database):
        self.database = database


    def add_entry(self, entry: StudySession) -> int:
        return self.database.add_study_session(entry)

    def add_subject(self, subject: Subject) -> int:
        return self.database.add_subject(subject)
    
    def get_subID_by_name(self, name: str) -> int | None:
        return self.database.get_subject_id_by_name(name)
    
    def get_all_subjects(self):
        # returns list of tuples (id, name, credits)
        return self.database.get_all_subjects()
    
    def get_last_entries(self, limit=10):
        return self.database.get_last_entries(limit)

    def get_subject_details(self, name: str):
        return self.database.get_subject_by_name(name)