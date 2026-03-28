from datetime import datetime, date
from PySide6.QtCore import Signal
from core.viewmodels.base_viewmodel import BaseViewModel
from core.models import StudySession

class SessionViewModel(BaseViewModel):
    """
    Handles all logic related to study sessions and history.
    """
    entries_changed = Signal()

    def __init__(self, repository):
        super().__init__(repository)

    def add_entry(self, subject, date_str, start_time_str, end_time_str, notes, quality=3):
        if not subject or not date_str or not start_time_str or not end_time_str:
            raise ValueError("All fields are required.")
        
        try:
            # Convert strings to Value Objects early
            # Expected formats: date_str="YYYY-MM-DD", time_str="HH:mm:ss"
            entry_date = date.fromisoformat(date_str)
            start_time = datetime.strptime(f"{date_str} {start_time_str}", "%Y-%m-%d %H:%M:%S")
            end_time = datetime.strptime(f"{date_str} {end_time_str}", "%Y-%m-%d %H:%M:%S")
            
            if start_time >= end_time:
                raise ValueError("Start time must be before end time.")

            subject_id = self.repository.get_subject_id_by_name(subject)
            if not subject_id:
                 raise ValueError("Subject does not exist.")
            
            session = StudySession(
                id=None,
                subject_id=subject_id,
                date=entry_date,
                start_time=start_time,
                end_time=end_time,
                quality=int(quality),
                notes=notes or ""
            )

            self.repository.add_entry(session)
            self.entries_changed.emit()
        except ValueError as e:
            raise ValueError(f"Invalid format: {e}")
        except Exception as e:
            raise ValueError(f"Error saving entry: {e}")

    def get_last_entries(self, limit=10):
        try:
            return self.repository.get_last_entries(limit)
        except Exception as e:
            raise ValueError(f"An error occurred: {e}")

    def delete_entry(self, entry_id: int):
        try:
            self.repository.delete_entry(entry_id)
            self.entries_changed.emit()
        except Exception as e:
            raise ValueError(f"An error occurred: {e}")
    
    def get_entry_by_id(self, entry_id: int) -> dict:
        try:
            session = self.repository.get_entry_by_id(entry_id)
            if not session:
                return {}
            
            # Convert objects back to strings ONLY for the UI layer
            return {
                "id": session.id,
                "subject_id": session.subject_id,
                "date": session.date.isoformat(),
                "start_time": session.start_time.strftime("%H:%M:%S"),
                "end_time": session.end_time.strftime("%H:%M:%S"),
                "quality": session.quality,
                "notes": session.notes
            }
        except Exception as e:
            raise ValueError(f"An error occurred: {e}")
        
    def modify_entry(self, entry_id: int, subject: str, date_str: str, start_time_str: str, end_time_str: str, notes: str, quality: int):
        try:
            entry_date = date.fromisoformat(date_str)
            start_time = datetime.strptime(f"{date_str} {start_time_str}", "%Y-%m-%d %H:%M:%S")
            end_time = datetime.strptime(f"{date_str} {end_time_str}", "%Y-%m-%d %H:%M:%S")
            
            subject_id = self.repository.get_subject_id_by_name(subject)
            if not subject_id:
                 raise ValueError("Subject does not exist.")

            self.repository.sessions.modify_entry(entry_id, subject_id, entry_date, start_time, end_time, notes, quality)
            self.entries_changed.emit()
        except Exception as e:
            raise ValueError(f"An error occurred: {e}")

    def get_daily_stats(self, days=365):
        try:
            return self.repository.get_daily_stats(days)
        except Exception as e:
            raise ValueError(f"An error occurred: {e}")

    def get_entries_by_date(self, date_str: str):
        try:
            rows = self.repository.get_entries_by_date(date_str)
            keys = ["id", "subject_name", "start_time", "end_time", "quality", "notes"]
            return [{k: v for k, v in zip(keys, row)} for row in rows]
        except Exception as e:
            raise ValueError(f"An error occurred: {e}")
