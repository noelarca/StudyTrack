import sqlite3
from dataclasses import dataclass

@dataclass
class StudySession:
    id: int | None
    subject_id: int
    date: str
    start_time: str
    end_time: str
    quality: int
    notes: str = ""

@dataclass
class Subject:
    id: int | None
    name: str
    semester: int
    year: int
    credits: int = 0
    notes: str = ""

@dataclass
class Task:
    id: int | None
    subject_id: int
    title: str
    description: str = ""
    due_date: str | None = None
    priority: int = 2  # 1: Low, 2: Medium, 3: High
    is_completed: bool = False

class Database:
    def __init__(self, db_name="study_tracker.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        # migrate subjects table if schema is outdated
        cursor.execute("PRAGMA table_info(subjects)")
        cols = [row[1] for row in cursor.fetchall()]
        if cols and ("year" not in cols or "semester" not in cols or "credits" not in cols):
            cursor.execute("DROP TABLE IF EXISTS subjects")
            cols = []

        # create subjects table
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
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO subjects (name, semester, year, credits, notes) VALUES (?, ?, ?, ?, ?)
            """, (subject.name, subject.semester, subject.year, subject.credits, subject.notes))
            self.conn.commit()
            return cursor.lastrowid
        
    def add_entry(self, session: StudySession) -> int:
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO study_sessions (subject_id, date, start_time, end_time, quality, notes) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (session.subject_id, session.date, session.start_time, session.end_time, session.quality, session.notes))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_subject_id_by_name(self, name: str) -> int | None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM subjects WHERE name = ?", (name,))
        result = cursor.fetchone()
        return result[0] if result else None
    
    def get_all_subjects(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name, credits FROM subjects")
        return cursor.fetchall()
    
    def get_last_entries(self, limit=10):
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
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, name, semester, year, credits, notes "
            "FROM subjects WHERE name = ?", (name,))
        return cursor.fetchone()

    def get_subject_minor_stats(self, name: str):
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
    
    def modify_subject(self, subject_id: int, name: str, semester: int, year: int, credits: int, notes: str):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE subjects 
            SET name = ?, semester = ?, year = ?, credits = ?, notes = ?
            WHERE id = ?
        """, (name, semester, year, credits, notes, subject_id))
        self.conn.commit()

    def modify_entry(self, entry_id: int, subject_id: int, date: str, start_time: str, end_time: str, notes: str, quality: int):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE study_sessions 
            SET subject_id = ?, date = ?, start_time = ?, end_time = ?, notes = ?, quality = ?
            WHERE id = ?
        """, (subject_id, date, start_time, end_time, notes, quality, entry_id))
        self.conn.commit()
    
    def delete_subject(self, subject_id: int):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM study_sessions WHERE subject_id = ?", (subject_id,))
        cursor.execute("DELETE FROM tasks WHERE subject_id = ?", (subject_id,))
        cursor.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
        self.conn.commit()

    def delete_entry(self, entry_id: int):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM study_sessions WHERE id = ?", (entry_id,))
        self.conn.commit()

    def get_entry_by_id(self, entry_id:int) -> tuple:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, subject_id, date, start_time, end_time, quality, notes
            FROM study_sessions WHERE id = ?
        """, (entry_id,))                       
        return cursor.fetchone()

    def get_subject_stats_over_time(self, name: str, days=7):
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
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO tasks (subject_id, title, description, due_date, priority, is_completed)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (task.subject_id, task.title, task.description, task.due_date, task.priority, 1 if task.is_completed else 0))
        self.conn.commit()
        return cursor.lastrowid

    def get_tasks_by_subject(self, subject_id: int):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, subject_id, title, description, due_date, priority, is_completed
            FROM tasks WHERE subject_id = ?
            ORDER BY priority DESC, due_date ASC
        """, (subject_id,))
        return cursor.fetchall()

    def get_all_tasks(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT t.id, s.name, t.title, t.description, t.due_date, t.priority, t.is_completed
            FROM tasks t
            JOIN subjects s ON t.subject_id = s.id
            ORDER BY t.is_completed ASC, t.priority DESC, t.due_date ASC
        """)
        return cursor.fetchall()

    def update_task_status(self, task_id: int, is_completed: bool):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE tasks SET is_completed = ? WHERE id = ?
        """, (1 if is_completed else 0, task_id))
        self.conn.commit()

    def delete_task(self, task_id: int):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.conn.commit()