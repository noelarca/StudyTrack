from database import Database, Subject, StudySession, Task

class StudyRepository:
    """
    Acts as an abstraction layer between the Database and the ViewModel.
    Provides methods to manage study sessions, subjects, and tasks.
    """
    def __init__(self, database: Database):
        """
        Initializes the repository with a database instance.
        
        Args:
            database (Database): The database instance to use for data operations.
        """
        self.database = database

    def add_entry(self, entry: StudySession) -> int:
        """
        Adds a new study session entry.
        
        Args:
            entry (StudySession): The session object to add.
            
        Returns:
            int: The ID of the newly created entry.
        """
        return self.database.add_entry(entry)

    def add_subject(self, subject: Subject) -> int:
        """
        Adds a new subject.
        
        Args:
            subject (Subject): The subject object to add.
            
        Returns:
            int: The ID of the newly created subject.
        """
        return self.database.add_subject(subject)
    
    def get_subject_id_by_name(self, name: str) -> int | None:
        """
        Retrieves a subject's ID based on its name.
        
        Args:
            name (str): The name of the subject.
            
        Returns:
            int | None: The subject ID if found, otherwise None.
        """
        return self.database.get_subject_id_by_name(name)
    
    def get_all_subjects(self):
        """
        Retrieves all subjects from the database.
        
        Returns:
            list: A list of tuples (id, name, credits).
        """
        return self.database.get_all_subjects()
    
    def get_last_entries(self, limit=10):
        """
        Retrieves the most recent study sessions.
        
        Args:
            limit (int): Max number of entries to retrieve.
            
        Returns:
            list: List of recent session data.
        """
        return self.database.get_last_entries(limit)

    def get_subject_details(self, name: str):
        """
        Retrieves comprehensive details and basic stats for a subject.
        Combines basic info with total hours and average quality.
        
        Args:
            name (str): The subject name.
            
        Returns:
            tuple: Combined subject information.
        """
        details = self.database.get_subject_by_name(name) + self.database.get_subject_minor_stats(name)
        return details
    
    def modify_subject(self, subject_id: int, name: str, semester: int, year: int, credits: int, notes: str):
        """
        Updates an existing subject's information.
        
        Args:
            subject_id (int): Subject identifier.
            name (str): New name.
            semester (int): New semester.
            year (int): New year.
            credits (int): New credit value.
            notes (str): New notes.
        """
        self.database.modify_subject(subject_id, name, semester, year, credits, notes)

    def delete_subject(self, subject_id: int):
        """
        Deletes a subject and its related data.
        
        Args:
            subject_id (int): Subject identifier.
        """
        self.database.delete_subject(subject_id)

    def delete_entry(self, entry_id: int):
        """
        Deletes a single study session entry.
        
        Args:
            entry_id (int): Session entry identifier.
        """
        self.database.delete_entry(entry_id)

    def get_entry_by_id(self, entry_id: int) -> tuple:
        """
        Retrieves a single study session entry by ID.
        
        Args:
            entry_id (int): Session entry identifier.
            
        Returns:
            tuple: Entry data.
        """
        return self.database.get_entry_by_id(entry_id)
    
    def modify_entry(self, entry_id: int, subject: str, date: str, start_time: str, end_time: str, notes: str, quality: int):
        """
        Updates an existing study session entry.
        Validates the subject name before proceeding.
        
        Args:
            entry_id (int): Entry identifier.
            subject (str): Subject name.
            date (str): New date.
            start_time (str): New start time.
            end_time (str): New end time.
            notes (str): New notes.
            quality (int): New quality rating.
            
        Raises:
            ValueError: If the subject name does not correspond to an existing subject.
        """
        subject_id = self.get_subject_id_by_name(subject)
        if subject_id is None:
            raise ValueError("Subject does not exist.")
        self.database.modify_entry(entry_id, subject_id, date, start_time, end_time, notes, quality)

    def get_subject_quality_distribution(self, name: str):
        """
        Retrieves the frequency of each quality rating for a subject.
        
        Args:
            name (str): Subject name.
            
        Returns:
            dict: Mapping of quality level to count.
        """
        return self.database.get_subject_quality_distribution(name)

    def get_subject_stats_over_time(self, name: str, days=7):
        """
        Retrieves study hours per day for a subject over a period.
        
        Args:
            name (str): Subject name.
            days (int): Period in days.
            
        Returns:
            list: List of (date, total_hours) tuples.
        """
        return self.database.get_subject_stats_over_time(name, days)

    def get_subject_streak(self, name: str):
        """
        Retrieves the current study streak for a subject.
        """
        return self.database.get_subject_streak(name)

    def get_entries_by_date(self, date_str: str):
        """
        Retrieves all sessions for a specific date.
        
        Args:
            date_str (str): Date in YYYY-MM-DD format.
            
        Returns:
            list: List of sessions for that date.
        """
        return self.database.get_entries_by_date(date_str)

    # --- TASK METHODS ---
    def add_task(self, task: Task) -> int:
        """
        Adds a new task.
        
        Args:
            task (Task): Task object to add.
            
        Returns:
            int: The ID of the newly created task.
        """
        return self.database.add_task(task)

    def get_tasks_by_subject(self, subject_id: int):
        """
        Retrieves all tasks for a specific subject.
        
        Args:
            subject_id (int): Subject identifier.
            
        Returns:
            list: List of tasks for the subject.
        """
        return self.database.get_tasks_by_subject(subject_id)

    def get_all_tasks(self):
        """
        Retrieves all tasks across all subjects.
        
        Returns:
            list: List of all tasks.
        """
        return self.database.get_all_tasks()

    def update_task_status(self, task_id: int, is_completed: bool):
        """
        Updates a task's completion status.

        Args:
            task_id (int): Task identifier.
            is_completed (bool): New status.
        """
        self.database.update_task_status(task_id, is_completed)

    def update_task(self, task_id: int, subject_id: int, title: str, description: str, due_date: str, priority: int):
        """
        Updates an existing task's information.
        """
        self.database.modify_task(task_id, subject_id, title, description, due_date, priority)

    def get_task_by_id(self, task_id: int):
        """
        Retrieves a single task by its ID.
        """
        return self.database.get_task_by_id(task_id)

    def delete_task(self, task_id: int):
        """
        Deletes a task.
        
        Args:
            task_id (int): Task identifier.
        """
        self.database.delete_task(task_id)
