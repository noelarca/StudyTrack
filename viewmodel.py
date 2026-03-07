from datetime import datetime
from PySide6.QtCore import QObject, Signal
from database import Subject, StudySession, Task

class ViewModel(QObject):
    """
    The ViewModel acts as the intermediary between the UI (View) and the Repository.
    It handles business logic, data validation, and provides signals to notify
    the UI of changes in the underlying data.
    """
    # Signals to notify the UI when data changes
    subjects_changed = Signal()
    entries_changed = Signal()
    tasks_changed = Signal()

    def __init__(self, repository):
        """
        Initializes the ViewModel with a repository instance.
        
        Args:
            repository (StudyRepository): The repository instance for data operations.
        """
        super().__init__()
        self.repository = repository

    def add_entry(self, subject, date, start_time, end_time, notes, quality=3):
        """
        Validates and adds a new study session entry.
        
        Args:
            subject (str): Name of the subject.
            date (str): Date of the session (YYYY-MM-DD).
            start_time (str): Start time (HH:mm:ss).
            end_time (str): End time (HH:mm:ss).
            notes (str): Session notes.
            quality (int): Quality rating (default 3).
            
        Raises:
            ValueError: If validation fails or an error occurs during saving.
        """
        # Data validity checks
        if not subject:
            raise ValueError("Subject cannot be empty.")
        
        if not date:
            raise ValueError("Date cannot be empty.")
        
        if not start_time or not end_time:
            raise ValueError("Start time and end time cannot be empty.")
        
        if start_time >= end_time:
            raise ValueError("Start time must be before end time.")

        # Ensure subject exists
        subjects = self.repository.get_all_subjects() or []
        # Repository returns list of tuples (id, name) — check names
        names = [row[1] if isinstance(row, (tuple, list)) and len(row) > 1 else str(row) for row in subjects]
        if subject not in names:
            raise ValueError("Subject does not exist. Please add it before creating an entry.")
        
        # Create session object and call repository
        try:
            subject_id = self.repository.get_subject_id_by_name(subject)
            # Store times as full timestamp strings (date + time) for reliable julianday calculations
            start_ts = f"{date} {start_time}"
            end_ts = f"{date} {end_time}"

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
            # Notify UI listeners
            self.entries_changed.emit()

        except ValueError as e:
            raise ValueError(f"Format must be HH:mm:ss. Error: {e}")
        except Exception as e:
            raise ValueError(f"An error occurred while saving entry: {e}")

    def add_subject(self, name, semester, year, credits=0, notes=""):
        """
        Validates and adds a new study subject.
        
        Args:
            name (str): Subject name.
            semester (int): Semester (1 or 2).
            year (int): Academic year.
            credits (int): Credit value (default 0).
            notes (str): Subject notes.
            
        Raises:
            ValueError: If validation fails or an error occurs.
        """
        # Data validity checks
        if semester not in [1, 2]:
            raise ValueError("Semester must be 1 or 2.")
        if year < 1:
            raise ValueError("Year must be a positive integer.")
        if credits < 0:
            raise ValueError("Credits must be a non-negative integer.")
        if not name:
            raise ValueError("Subject name cannot be empty.")
        
        # Create Subject dataclass and call repository
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
            # Notify UI listeners
            self.subjects_changed.emit()

        except Exception as e:  
            raise ValueError(f"An error occurred while adding the subject: {e}")
        
    def get_subjects(self):
        """
        Retrieves a list of all subjects.
        
        Returns:
            list: List of subject tuples from the repository.
            
        Raises:
            ValueError: If an error occurs during retrieval.
        """
        try:
            subjects = self.repository.get_all_subjects()
            if not subjects:
                return []
            return subjects
        except Exception as e:
            raise ValueError(f"An error occurred while fetching subjects: {e}")
        
    def get_last_entries(self, limit=10):
        """
        Retrieves the most recent study session entries.
        
        Args:
            limit (int): Max number of entries to retrieve.
            
        Returns:
            list: List of recent session data.
            
        Raises:
            ValueError: If an error occurs.
        """
        try:
            entries = self.repository.get_last_entries(limit)
            return entries
        except Exception as e:
            raise ValueError(f"An error occurred while fetching last entries: {e}")

    def select_subject(self, subject: str):
        """
        Sets the currently active/selected subject in the application state.
        
        Args:
            subject (str): The name of the subject to select.
        """
        self.selected_subject = subject

    def get_subject_details(self, subject: str) -> dict:
        """
        Retrieves detailed information and stats for a specific subject.
        
        Args:
            subject (str): Subject name.
            
        Returns:
            dict: Dictionary of subject properties and statistics.
            
        Raises:
            ValueError: If an error occurs.
        """
        try:
            row = self.repository.get_subject_details(subject)
            if not row:
                return {}
            # Map database row to dictionary keys
            keys = ["id", "name", "semester", "year", "credits", "notes", "total_hours", "avg_quality"]
            return {k: v for k, v in zip(keys, row)}
        except Exception as e:
            raise ValueError(f"An error occurred while fetching subject details: {e}")
        
    def update_subject(self, subject_id: int, name: str, semester: int, year: int, credits: int, notes: str):
        """
        Updates an existing subject's details.
        
        Args:
            subject_id (int): Subject identifier.
            name (str): New name.
            semester (int): New semester.
            year (int): New year.
            credits (int): New credits.
            notes (str): New notes.
            
        Raises:
            ValueError: If an error occurs.
        """
        try:
            self.repository.modify_subject(subject_id, name, semester, year, credits, notes)
            # Notify UI listeners
            self.subjects_changed.emit()
        except Exception as e:
            raise ValueError(f"An error occurred while updating the subject: {e}")
    
    def delete_subject(self, subject_id: int):
        """
        Deletes a subject and its associated data.
        
        Args:
            subject_id (int): Subject identifier.
            
        Raises:
            ValueError: If an error occurs.
        """
        try:
            self.repository.delete_subject(subject_id)
            # Notify UI listeners
            self.subjects_changed.emit()
        except Exception as e:
            raise ValueError(f"An error occurred while deleting the subject: {e}")
    
    def delete_entry(self, entry_id: int):
        """
        Deletes a specific study session entry.
        
        Args:
            entry_id (int): Entry identifier.
            
        Raises:
            ValueError: If an error occurs.
        """
        try:
            self.repository.delete_entry(entry_id)
            # Notify UI listeners
            self.entries_changed.emit()
        except Exception as e:
            raise ValueError(f"An error occurred while deleting the entry: {e}")
    
    def get_subject_id_by_name(self, name: str) -> int | None:
        """
        Gets the ID for a given subject name.
        
        Args:
            name (str): Subject name.
            
        Returns:
            int | None: Subject ID or None.
            
        Raises:
            ValueError: If an error occurs.
        """
        try:
            return self.repository.get_subject_id_by_name(name)
        except Exception as e:
            raise ValueError(f"An error occurred while fetching subject ID: {e}")
        
    def get_entry_by_id(self, entry_id: int) -> dict:
        """
        Retrieves data for a single study session entry.
        
        Args:
            entry_id (int): Entry identifier.
            
        Returns:
            dict: Dictionary of entry properties.
            
        Raises:
            ValueError: If an error occurs.
        """
        try:
            row = self.repository.get_entry_by_id(entry_id)
            if not row:
                return {}
            keys = ["id", "subject_id", "date", "start_time", "end_time", "quality", "notes"]
            return {k: v for k, v in zip(keys, row)}
        except Exception as e:
            raise ValueError(f"An error occurred while fetching entry details: {e}")
        
    def modify_entry(self, entry_id: int, subject: str, date: str, start_time: str, end_time: str, notes: str, quality: int):
        """
        Updates an existing study session entry.
        
        Args:
            entry_id (int): Entry identifier.
            subject (str): Subject name.
            date (str): New date.
            start_time (str): New start time.
            end_time (str): New end time.
            notes (str): New notes.
            quality (int): New quality rating.
            
        Raises:
            ValueError: If an error occurs or subject doesn't exist.
        """
        try:
            subject_id = self.get_subject_id_by_name(subject)
            if subject_id is None:
                raise ValueError("Subject does not exist.")
            
            self.repository.modify_entry(entry_id, subject, date, start_time, end_time, notes, quality)
            # Notify UI listeners
            self.entries_changed.emit()
        except Exception as e:
            raise ValueError(f"An error occurred while modifying the entry: {e}")

    def get_subject_quality_distribution(self, name: str):
        """
        Retrieves the distribution of session quality for a subject.
        
        Args:
            name (str): Subject name.
            
        Returns:
            dict: Mapping of quality (1-5) to frequency.
            
        Raises:
            ValueError: If an error occurs.
        """
        try:
            return self.repository.get_subject_quality_distribution(name)
        except Exception as e:
            raise ValueError(f"An error occurred while fetching quality distribution: {e}")

    def get_subject_stats_over_time(self, name: str, days=7):
        """
        Retrieves time-series study data for a subject.
        
        Args:
            name (str): Subject name.
            days (int): Time period.
            
        Returns:
            list: List of (date, hours) tuples.
            
        Raises:
            ValueError: If an error occurs.
        """
        try:
            return self.repository.get_subject_stats_over_time(name, days)
        except Exception as e:
            raise ValueError(f"An error occurred while fetching stats: {e}")

    def get_daily_stats(self, days=365):
        """
        Retrieves aggregated daily study stats for all subjects.
        
        Args:
            days (int): Time period.
            
        Returns:
            list: List of (date, total_hours) tuples.
            
        Raises:
            ValueError: If an error occurs.
        """
        try:
            return self.repository.database.get_daily_stats(days)
        except Exception as e:
            raise ValueError(f"An error occurred while fetching daily stats: {e}")

    def get_entries_by_date(self, date_str: str):
        """
        Retrieves all sessions occurring on a specific date.
        
        Args:
            date_str (str): Target date (YYYY-MM-DD).
            
        Returns:
            list: List of session dictionaries.
            
        Raises:
            ValueError: If an error occurs.
        """
        try:
            rows = self.repository.get_entries_by_date(date_str)
            keys = ["id", "subject_name", "start_time", "end_time", "quality", "notes"]
            return [{k: v for k, v in zip(keys, row)} for row in rows]
        except Exception as e:
            raise ValueError(f"An error occurred while fetching entries for date: {e}")

    # --- TASK METHODS ---
    def add_task(self, subject_name, title, description="", due_date=None, priority=2):
        """
        Validates and adds a new task for a subject.
        
        Args:
            subject_name (str): Subject name.
            title (str): Task title.
            description (str): Task description.
            due_date (str): Due date (YYYY-MM-DD).
            priority (int): Task priority.
            
        Raises:
            ValueError: If title is empty, subject doesn't exist, or an error occurs.
        """
        if not title:
            raise ValueError("Task title cannot be empty.")
        
        subject_id = self.get_subject_id_by_name(subject_name)
        if not subject_id:
            raise ValueError("Subject does not exist.")

        try:
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
        """
        Retrieves all tasks for a specific subject.
        
        Args:
            subject_name (str): Subject name.
            
        Returns:
            list: List of tasks.
            
        Raises:
            ValueError: If an error occurs.
        """
        subject_id = self.get_subject_id_by_name(subject_name)
        if not subject_id:
            return []
        try:
            return self.repository.get_tasks_by_subject(subject_id)
        except Exception as e:
            raise ValueError(f"An error occurred while fetching tasks: {e}")

    def get_all_tasks(self):
        """
        Retrieves all tasks across all subjects.
        
        Returns:
            list: List of all tasks.
            
        Raises:
            ValueError: If an error occurs.
        """
        try:
            return self.repository.get_all_tasks()
        except Exception as e:
            raise ValueError(f"An error occurred while fetching all tasks: {e}")

    def toggle_task_completion(self, task_id, is_completed):
        """
        Toggles the completion status of a task.
        
        Args:
            task_id (int): Task identifier.
            is_completed (bool): New completion status.
            
        Raises:
            ValueError: If an error occurs.
        """
        try:
            self.repository.update_task_status(task_id, is_completed)
            self.tasks_changed.emit()
        except Exception as e:
            raise ValueError(f"An error occurred while updating task: {e}")

    def delete_task(self, task_id):
        """
        Deletes a task.
        
        Args:
            task_id (int): Task identifier.
            
        Raises:
            ValueError: If an error occurs.
        """
        try:
            self.repository.delete_task(task_id)
            self.tasks_changed.emit()
        except Exception as e:
            raise ValueError(f"An error occurred while deleting task: {e}")
