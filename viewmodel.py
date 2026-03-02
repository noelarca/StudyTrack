from datetime import datetime
from PySide6.QtCore import QObject, Signal


class ViewModel(QObject):
    subjects_changed = Signal()
    entries_changed = Signal()

    def __init__(self, repository):
        super().__init__()
        self.repository = repository

    def add_entry(self, subject, date, start_time, end_time, notes, quality=3):

        # Controlli di validità dei dati
        if not subject:
            raise ValueError("Subject cannot be empty.")
        
        if not date:
            raise ValueError("Date cannot be empty.")
        
        if not start_time or not end_time:
            raise ValueError("Start time and end time cannot be empty.")
        
        if start_time >= end_time:
            raise ValueError("Start time must be before end time.")

        # ensure subject exists
        subjects = self.repository.get_all_subjects() or []
        # repository returns list of tuples (id, name) — check names
        names = [row[1] if isinstance(row, (tuple, list)) and len(row) > 1 else str(row) for row in subjects]
        if subject not in names:
            raise ValueError("Subject does not exist. Please add it before creating an entry.")
        
        # Creazione del dizionario del soggetto e chiamata al repository
        try:
            from database import StudySession

            subject_id = self.repository.get_subID_by_name(subject)
            # store times as full timestamp strings (date + time) for reliable julianday calculations
            start_ts = f"{date} {start_time}:00"
            end_ts = f"{date} {end_time}:00"

            session = StudySession(
                id=None,
                subject_id=subject_id,
                date=date,
                start_time=start_ts,
                end_time=end_ts,
                quality=int(quality),
                notes=notes or ""
            )

            self.repository.add_entry(session)
            # notify UI listeners
            self.entries_changed.emit()

        except ValueError as e:
            raise ValueError(f"Format must be HH:MM. Error: {e}")
        except Exception as e:
            raise ValueError(f"An error occurred while saving entry: {e}")

    def add_subject(self, name, semester, year, credits=0, notes=""):

        # Controlli di validità dei dati
        if semester not in [1, 2]:
            raise ValueError("Semester must be 1 or 2.")
        if year < 1:
            raise ValueError("Year must be a positive integer.")
        if credits < 0:
            raise ValueError("Credits must be a non-negative integer.")
        if not name:
            raise ValueError("Subject name cannot be empty.")
        
        # Creazione del Subject dataclass e chiamata al repository
        try:
            from database import Subject

            subj = Subject(
                id=None,
                name=name,
                semester=semester,
                year=year,
                credits=credits,
                notes=notes
            )
            self.repository.add_subject(subj)
            # notify UI listeners
            self.subjects_changed.emit()

        except Exception as e:  
            raise ValueError(f"An error occurred while adding the subject: {e}")
        
    def get_subjects(self):
        """Return a list of subjects from the repository.

        The repository method returns whatever the database returns (usually a
        list of tuples). The UI layers are responsible for interpreting the
        format. If there are no subjects an empty list is returned instead of a
        string; this simplifies client code.
        """
        try:
            subjects = self.repository.get_all_subjects()
            if not subjects:
                return []
            return subjects
        except Exception as e:
            raise ValueError(f"An error occurred while fetching subjects: {e}")
        
    def get_last_entries(self, limit=10):
        try:
            entries = self.repository.get_last_entries(limit)
            return entries
        except Exception as e:
            raise ValueError(f"An error occurred while fetching last entries: {e}")

    # ---- new methods for subject details support ----
    def select_subject(self, subject: str):
        """Keep track of the currently selected subject."""
        self.selected_subject = subject

    def get_subject_details(self, subject: str) -> dict:
        """
        Return a dictionary of properties for the given subject.

        The repository is expected to return a row/tuple; convert it to a dict
        so that the view layer can iterate over ``items()``.
        """
        try:
            row = self.repository.get_subject_details(subject)
            if not row:
                return {}
            # depending on repository implementation the row may contain
            # (id, name, semester, year, credits, notes) or similar
            keys = ["id", "name", "semester", "year", "credits", "notes", "total_hours", "avg_quality"]
            return {k: v for k, v in zip(keys, row)}
        except Exception as e:
            raise ValueError(f"An error occurred while fetching subject details: {e}")
        
    def update_subject(self, subject_id: int, name: str, semester: int, year: int, credits: int, notes: str):
        try:
            self.repository.modify_subject(subject_id, name, semester, year, credits, notes)
            # notify UI listeners
            self.subjects_changed.emit()
        except Exception as e:
            raise ValueError(f"An error occurred while updating the subject: {e}")
    
    def delete_subject(self, subject_id: int):
        try:
            self.repository.delete_subject(subject_id)
            # notify UI listeners
            self.subjects_changed.emit()
        except Exception as e:
            raise ValueError(f"An error occurred while deleting the subject: {e}")
    
    def get_subject_id_by_name(self, name: str) -> int | None:
        try:
            return self.repository.get_subID_by_name(name)
        except Exception as e:
            raise ValueError(f"An error occurred while fetching subject ID: {e}")   