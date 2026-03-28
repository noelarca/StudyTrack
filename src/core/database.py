import sqlite3
import os
import sys
from core.models import StudySession, Subject, Task

class Database:
    """
    Handles direct interactions with the SQLite database.
    Responsible for table creation, connection management, and safe schema migrations.
    """
    CURRENT_VERSION = 1

    def __init__(self, db_name="study_tracker.db"):
        if not os.path.isabs(db_name):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            db_name = os.path.join(base_dir, db_name)
        
        try:
            self.conn = sqlite3.connect(db_name)
            self.initialize_schema()
        except sqlite3.OperationalError as e:
            print(f"Database Error: {e}")
            raise

    def initialize_schema(self):
        """
        Initializes the database and handles migrations from one version to another.
        """
        cursor = self.conn.cursor()
        
        # 1. Create the version table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY
            )
        """)
        
        # 2. Get current version
        cursor.execute("SELECT version FROM schema_version")
        row = cursor.fetchone()
        
        if row is None:
            # New database or legacy (pre-versioning)
            # Check if tables exist to determine if it's legacy
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='subjects'")
            if cursor.fetchone():
                # Legacy database found. Reconcile to Version 1.
                self._migrate_legacy_to_v1(cursor)
            else:
                # Brand new database. Create everything and set to Version 1.
                self._create_v1_tables(cursor)
                cursor.execute("INSERT INTO schema_version (version) VALUES (1)")
        else:
            current_db_version = row[0]
            # Here is where future migrations would go:
            # if current_db_version < 2:
            #     self._migrate_v1_to_v2(cursor)
            pass

        self.conn.commit()

    def _create_v1_tables(self, cursor):
        """Creates the baseline schema (Version 1)."""
        # Subjects
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
        # Study Sessions
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
        # Tasks
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

    def _migrate_legacy_to_v1(self, cursor):
        """
        Handles databases from before the versioning system was added.
        Instead of DROP TABLE, we check and add missing columns.
        """
        # Check Subjects table
        cursor.execute("PRAGMA table_info(subjects)")
        cols = [row[1] for row in cursor.fetchall()]
        
        # Add missing columns safely if they don't exist
        if "semester" not in cols:
            cursor.execute("ALTER TABLE subjects ADD COLUMN semester INTEGER NOT NULL DEFAULT 1")
        if "year" not in cols:
            cursor.execute("ALTER TABLE subjects ADD COLUMN year INTEGER NOT NULL DEFAULT 2024")
        if "credits" not in cols:
            cursor.execute("ALTER TABLE subjects ADD COLUMN credits INTEGER NOT NULL DEFAULT 0")

        # Check Tasks table
        cursor.execute("PRAGMA table_info(tasks)")
        task_cols = [row[1] for row in cursor.fetchall()]
        if "due_date" not in task_cols:
            cursor.execute("ALTER TABLE tasks ADD COLUMN due_date TEXT")
        if "priority" not in task_cols:
            cursor.execute("ALTER TABLE tasks ADD COLUMN priority INTEGER DEFAULT 2")

        # Now that it's reconciled, set version to 1
        cursor.execute("INSERT INTO schema_version (version) VALUES (1)")
