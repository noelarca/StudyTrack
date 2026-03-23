import sqlite3
import os
import sys
from dataclasses import dataclass

@dataclass
class StudySession:
    # ... dataclass content ...
    id: int | None
    subject_id: int
    date: str
    start_time: str
    end_time: str
    quality: int
    notes: str = ""

@dataclass
class Subject:
    # ... dataclass content ...
    id: int | None
    name: str
    semester: int
    year: int
    credits: int = 0
    notes: str = ""

@dataclass
class Task:
    # ... dataclass content ...
    id: int | None
    subject_id: int
    title: str
    description: str = ""
    due_date: str | None = None
    priority: int = 2  # 1: Low, 2: Medium, 3: High
    is_completed: bool = False

class Database:
    """
    Handles all direct interactions with the SQLite database.
    Responsible for table creation, migrations, and CRUD operations for 
    subjects, study sessions, and tasks.
    """
    def __init__(self, db_name="study_tracker.db"):
        """
        Initializes the database connection and ensures tables exist.
        Uses an absolute path to ensure the database is always in the script's directory.
        
        Args:
            db_name (str): Path to the SQLite database file.
        """
        # Ensure the database is created in the same directory as the script
        if not os.path.isabs(db_name):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            db_name = os.path.join(base_dir, db_name)
        
        try:
            self.conn = sqlite3.connect(db_name)
            self.create_tables()
        except sqlite3.OperationalError as e:
            print(f"Errore critico del database: {e}")
            print(f"Tentativo di apertura a: {db_name}")
            raise

    def create_tables(self):
        """
        Creates the necessary tables if they don't exist and handles simple migrations.
        Includes tables for subjects, study_sessions, and tasks.
        """
        cursor = self.conn.cursor()
        
        # Check and migrate subjects table if schema is outdated
        cursor.execute("PRAGMA table_info(subjects)")
        cols = [row[1] for row in cursor.fetchall()]
        if cols and ("year" not in cols or "semester" not in cols or "credits" not in cols):
            cursor.execute("DROP TABLE IF EXISTS subjects")
            cols = []

        # Create subjects table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                semester INTEGER NOT NULL,
                year INTEGER NOT NULL,
                credits INTEGER NOT NULL DEFAULT 0,
                notes TEXT
            )
        """)

        # Create study_sessions table with a generated column for duration
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS study_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                duration_hours REAL GENERATED ALWAYS AS (
                    (julianday(end_time) - julianday(start_time)) * 24.0) STORED,
                quality INTEGER NOT NULL,
                notes TEXT,
                FOREIGN KEY (subject_id) REFERENCES subjects(id)
            )
        """)

        # Migration/Creation for tasks table
        cursor.execute("PRAGMA table_info(tasks)")
        task_cols = [row[1] for row in cursor.fetchall()]
        if task_cols and ("due_date" not in task_cols or "priority" not in task_cols):
            cursor.execute("DROP TABLE IF EXISTS tasks")

        # Create tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                due_date TEXT,
                priority INTEGER DEFAULT 2,
                is_completed INTEGER DEFAULT 0,
                FOREIGN KEY (subject_id) REFERENCES subjects(id)
            )
        """)
        self.conn.commit()

    def add_subject(self, subject: Subject) -> int:
        """
        Adds a new subject to the database.
        
        Args:
            subject (Subject): The subject object to add.
            
        Returns:
            int: The ID of the newly inserted subject.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO subjects (name, semester, year, credits, notes) VALUES (?, ?, ?, ?, ?)
        """, (subject.name, subject.semester, subject.year, subject.credits, subject.notes))
        self.conn.commit()
        return cursor.lastrowid
        
    def add_entry(self, session: StudySession) -> int:
        """
        Adds a new study session entry to the database.
        
        Args:
            session (StudySession): The session object to add.
            
        Returns:
            int: The ID of the newly inserted session.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO study_sessions (subject_id, date, start_time, end_time, quality, notes) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (session.subject_id, session.date, session.start_time, session.end_time, session.quality, session.notes))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_subject_id_by_name(self, name: str) -> int | None:
        """
        Retrieves the ID of a subject given its name.
        
        Args:
            name (str): The name of the subject.
            
        Returns:
            int | None: The subject ID if found, otherwise None.
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM subjects WHERE name = ?", (name,))
        result = cursor.fetchone()
        return result[0] if result else None
    
    def get_all_subjects(self):
        """
        Retrieves a list of all subjects.
        
        Returns:
            list: A list of tuples containing (id, name, credits).
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name, credits FROM subjects")
        return cursor.fetchall()
    
    def get_last_entries(self, limit=10):
        """
        Retrieves the most recent study sessions.
        
        Args:
            limit (int): The maximum number of entries to return.
            
        Returns:
            list: A list of tuples containing session details and subject name.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT ss.id, s.name, ss.date, 
                   (julianday(ss.end_time) - julianday(ss.start_time)) * 24.0 AS duration_hours,
                   ss.quality, ss.notes
            FROM study_sessions ss
            JOIN subjects s ON ss.subject_id = s.id
            ORDER BY ss.date DESC, ss.start_time DESC
            LIMIT ?
        """, (limit,))
        return cursor.fetchall()
    
    def get_subject_by_name(self, name: str):
        """
        Retrieves full subject details by name.
        
        Args:
            name (str): The name of the subject.
            
        Returns:
            tuple | None: Subject data tuple or None if not found.
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, name, semester, year, credits, notes "
            "FROM subjects WHERE name = ?", (name,))
        return cursor.fetchone()

    def get_subject_minor_stats(self, name: str):
        """
        Calculates basic statistics for a subject (total hours and average quality).
        
        Args:
            name (str): The name of the subject.
            
        Returns:
            tuple: (total_hours, avg_quality).
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                IFNULL(SUM((julianday(end_time) - julianday(start_time)) * 24.0), 0) AS total_hours,
                IFNULL(AVG(quality), 0) AS avg_quality
            FROM study_sessions ss
            JOIN subjects s ON ss.subject_id = s.id
            WHERE s.name = ?
        """, (name,))
        return cursor.fetchone()
    
    def get_subject_streak(self, name: str) -> int:
        """
        Calculates the current study streak (consecutive days) for a subject.
        
        Args:
            name (str): Subject name.
            
        Returns:
            int: Number of consecutive days.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT DISTINCT date FROM study_sessions ss
            JOIN subjects s ON ss.subject_id = s.id
            WHERE s.name = ?
            ORDER BY date DESC
        """, (name,))
        
        rows = cursor.fetchall()
        if not rows:
            return 0
        
        from datetime import datetime, timedelta
        
        dates = [datetime.strptime(r[0], "%Y-%m-%d").date() for r in rows]
        today = datetime.now().date()
        
        streak = 0
        current_check = today
        
        # If the most recent study date is not today or yesterday, streak is 0
        if dates[0] < today - timedelta(days=1):
            return 0
            
        # Start from the most recent study date
        if dates[0] == today:
            streak = 1
            current_check = today - timedelta(days=1)
        elif dates[0] == today - timedelta(days=1):
            streak = 1
            current_check = today - timedelta(days=2)
        else:
            return 0
            
        # Check previous dates
        for i in range(1 if dates[0] >= today - timedelta(days=1) else 0, len(dates)):
            if dates[i] == current_check:
                streak += 1
                current_check -= timedelta(days=1)
            elif dates[i] > current_check:
                continue # Multiple sessions on same day already handled by DISTINCT
            else:
                break # Streak broken
                
        return streak

    def modify_subject(self, subject_id: int, name: str, semester: int, year: int, credits: int, notes: str):
        """
        Updates an existing subject's information.
        
        Args:
            subject_id (int): ID of the subject to update.
            name (str): New name.
            semester (int): New semester.
            year (int): New year.
            credits (int): New credit value.
            notes (str): New notes.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE subjects 
            SET name = ?, semester = ?, year = ?, credits = ?, notes = ?
            WHERE id = ?
        """, (name, semester, year, credits, notes, subject_id))
        self.conn.commit()

    def modify_entry(self, entry_id: int, subject_id: int, date: str, start_time: str, end_time: str, notes: str, quality: int):
        """
        Updates an existing study session entry.
        
        Args:
            entry_id (int): ID of the entry to update.
            subject_id (int): ID of the subject.
            date (str): New date.
            start_time (str): New start time.
            end_time (str): New end time.
            notes (str): New notes.
            quality (int): New quality rating.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE study_sessions 
            SET subject_id = ?, date = ?, start_time = ?, end_time = ?, notes = ?, quality = ?
            WHERE id = ?
        """, (subject_id, date, start_time, end_time, notes, quality, entry_id))
        self.conn.commit()
    
    def delete_subject(self, subject_id: int):
        """
        Deletes a subject and all associated study sessions and tasks.
        
        Args:
            subject_id (int): ID of the subject to delete.
        """
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM study_sessions WHERE subject_id = ?", (subject_id,))
        cursor.execute("DELETE FROM tasks WHERE subject_id = ?", (subject_id,))
        cursor.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
        self.conn.commit()

    def delete_entry(self, entry_id: int):
        """
        Deletes a single study session entry.
        
        Args:
            entry_id (int): ID of the entry to delete.
        """
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM study_sessions WHERE id = ?", (entry_id,))
        self.conn.commit()

    def get_entry_by_id(self, entry_id:int) -> tuple:
        """
        Retrieves a single study session entry by its ID.
        
        Args:
            entry_id (int): ID of the session.
            
        Returns:
            tuple: Entry data.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, subject_id, date, start_time, end_time, quality, notes
            FROM study_sessions WHERE id = ?
        """, (entry_id,))                       
        return cursor.fetchone()

    def get_subject_quality_distribution(self, name: str):
        """
        Retrieves the distribution of quality ratings for a subject.
        
        Args:
            name (str): Subject name.
            
        Returns:
            dict: {quality_level: count} mapping.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT ss.quality, COUNT(*)
            FROM study_sessions ss
            JOIN subjects s ON ss.subject_id = s.id
            WHERE s.name = ?
            GROUP BY ss.quality
        """, (name,))
        return dict(cursor.fetchall())

    def get_subject_stats_over_time(self, name: str, days=7):
        """
        Retrieves total study hours per day for a specific subject over a period.
        
        Args:
            name (str): Subject name.
            days (int): Number of past days to include.
            
        Returns:
            list: List of (date, total_hours) tuples.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT ss.date, SUM(ss.duration_hours)
            FROM study_sessions ss
            JOIN subjects s ON ss.subject_id = s.id
            WHERE s.name = ? AND ss.date >= date('now', ?)
            GROUP BY ss.date
            ORDER BY ss.date ASC
        """, (name, f"-{days} days"))
        return cursor.fetchall()

    def get_daily_stats(self, days=365):
        """
        Retrieves total study hours per day across all subjects.
        
        Args:
            days (int): Number of past days to include.
            
        Returns:
            list: List of (date, total_hours) tuples.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT date, SUM(duration_hours)
            FROM study_sessions
            WHERE date >= date('now', ?)
            GROUP BY date
            ORDER BY date ASC
        """, (f"-{days} days",))
        return cursor.fetchall()

    def get_entries_by_date(self, date_str: str):
        """
        Retrieves all study sessions for a specific date.
        
        Args:
            date_str (str): Date in YYYY-MM-DD format.
            
        Returns:
            list: List of sessions occurring on that date.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT ss.id, s.name, ss.start_time, ss.end_time, ss.quality, ss.notes
            FROM study_sessions ss
            JOIN subjects s ON ss.subject_id = s.id
            WHERE ss.date = ?
            ORDER BY ss.start_time ASC
        """, (date_str,))
        return cursor.fetchall()

    # --- TASK METHODS ---
    def add_task(self, task: Task) -> int:
        """
        Adds a new task to the database.
        
        Args:
            task (Task): Task object to add.
            
        Returns:
            int: ID of the newly inserted task.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO tasks (subject_id, title, description, due_date, priority, is_completed)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (task.subject_id, task.title, task.description, task.due_date, task.priority, 1 if task.is_completed else 0))
        self.conn.commit()
        return cursor.lastrowid

    def get_tasks_by_subject(self, subject_id: int):
        """
        Retrieves all tasks for a specific subject.
        
        Args:
            subject_id (int): Subject ID.
            
        Returns:
            list: List of tasks for that subject.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, subject_id, title, description, due_date, priority, is_completed
            FROM tasks WHERE subject_id = ?
            ORDER BY priority DESC, due_date ASC
        """, (subject_id,))
        return cursor.fetchall()

    def get_all_tasks(self):
        """
        Retrieves all tasks across all subjects, ordered by completion status, priority, and due date.
        
        Returns:
            list: List of all tasks.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT t.id, s.name, t.title, t.description, t.due_date, t.priority, t.is_completed
            FROM tasks t
            JOIN subjects s ON t.subject_id = s.id
            ORDER BY t.is_completed ASC, t.priority DESC, t.due_date ASC
        """)
        return cursor.fetchall()

    def update_task_status(self, task_id: int, is_completed: bool):
        """
        Updates the completion status of a task.
        
        Args:
            task_id (int): Task ID.
            is_completed (bool): New completion status.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE tasks SET is_completed = ? WHERE id = ?
        """, (1 if is_completed else 0, task_id))
        self.conn.commit()

    def delete_task(self, task_id: int):
        """
        Deletes a task from the database.
        
        Args:
            task_id (int): Task ID.
        """
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.conn.commit()

    def modify_task(self, task_id: int, subject_id: int, title: str, description: str, due_date: str, priority: int):
        """
        Updates an existing task's information.
        
        Args:
            task_id (int): Task ID.
            subject_id (int): ID of the subject.
            title (str): New title.
            description (str): New description.
            due_date (str): New due date.
            priority (int): New priority.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE tasks 
            SET subject_id = ?, title = ?, description = ?, due_date = ?, priority = ?
            WHERE id = ?
        """, (subject_id, title, description, due_date, priority, task_id))
        self.conn.commit()

    def get_task_by_id(self, task_id: int):
        """
        Retrieves a single task by its ID.
        
        Args:
            task_id (int): ID of the task.
            
        Returns:
            tuple: Task data.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT t.id, s.name, t.title, t.description, t.due_date, t.priority, t.is_completed
            FROM tasks t
            JOIN subjects s ON t.subject_id = s.id
            WHERE t.id = ?
        """, (task_id,))
        return cursor.fetchone()
