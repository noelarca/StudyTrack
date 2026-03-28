from PySide6.QtCore import Signal
from core.viewmodels.base_viewmodel import BaseViewModel
from core.models import Subject

class SubjectViewModel(BaseViewModel):
    """
    Handles all logic related to subject management and statistics.
    """
    subjects_changed = Signal()

    def __init__(self, repository):
        super().__init__(repository)

    def add_subject(self, name, semester, year, credits=0, notes=""):
        if semester not in [1, 2]:
            raise ValueError("Semester must be 1 or 2.")
        if year < 1:
            raise ValueError("Year must be a positive integer.")
        if credits < 0:
            raise ValueError("Credits must be a non-negative integer.")
        if not name:
            raise ValueError("Subject name cannot be empty.")
        
        try:
            subj = Subject(
                id=None,
                name=name,
                semester=semester,
                year=year,
                credits=credits,
                notes=notes
            )
            self.repository.add_subject(subj)
            self.subjects_changed.emit()
        except Exception as e:  
            raise ValueError(f"An error occurred while adding the subject: {e}")
        
    def get_subjects(self):
        try:
            # We still return tuples for now to keep UI compatibility,
            # or we can convert them here.
            subjects = self.repository.get_all_subjects()
            return [(s.id, s.name, s.credits) for s in subjects]
        except Exception as e:
            raise ValueError(f"An error occurred while fetching subjects: {e}")

    def get_subject_details(self, name: str) -> dict:
        try:
            details = self.repository.get_subject_details(name)
            if not details:
                return {}
            # Models make this much cleaner!
            return {
                "id": details.id,
                "name": details.name,
                "semester": details.semester,
                "year": details.year,
                "credits": details.credits,
                "notes": details.notes,
                "total_hours": details.total_hours,
                "avg_quality": details.avg_quality
            }
        except Exception as e:
            raise ValueError(f"An error occurred while fetching subject details: {e}")
        
    def update_subject(self, subject_id: int, name: str, semester: int, year: int, credits: int, notes: str):
        try:
            self.repository.modify_subject(subject_id, name, semester, year, credits, notes)
            self.subjects_changed.emit()
        except Exception as e:
            raise ValueError(f"An error occurred while updating the subject: {e}")
    
    def delete_subject(self, subject_id: int):
        try:
            self.repository.delete_subject(subject_id)
            self.subjects_changed.emit()
        except Exception as e:
            raise ValueError(f"An error occurred while deleting the subject: {e}")

    def get_subject_id_by_name(self, name: str) -> int | None:
        try:
            return self.repository.get_subject_id_by_name(name)
        except Exception as e:
            raise ValueError(f"An error occurred while fetching subject ID: {e}")

    def get_subject_quality_distribution(self, name: str):
        try:
            return self.repository.get_subject_quality_distribution(name)
        except Exception as e:
            raise ValueError(f"An error occurred while fetching quality distribution: {e}")

    def get_subject_stats_over_time(self, name: str, days=7):
        try:
            return self.repository.get_subject_stats_over_time(name, days)
        except Exception as e:
            raise ValueError(f"An error occurred while fetching stats: {e}")

    def get_subject_streak(self, name: str):
        try:
            return self.repository.get_subject_streak(name)
        except Exception as e:
            print(f"Error fetching streak: {e}")
            return 0

    def get_subject_progress(self, name: str):
        try:
            details = self.get_subject_details(name)
            if not details:
                return 0, 0
            
            total_hours = details.get("total_hours", 0)
            credits = details.get("credits", 0)
            target_hours = credits * 15
            
            if target_hours == 0:
                return 100, 0
            
            progress = (total_hours / target_hours) * 100
            return min(progress, 100), target_hours
        except Exception as e:
            print(f"Error calculating progress: {e}")
            return 0, 0
