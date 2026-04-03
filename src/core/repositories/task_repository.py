from datetime import date
from core.database import Database
from core.models import Task

class TaskRepository:
    def __init__(self, database: Database):
        self.database = database

    def add_task(self, task: Task) -> int:
        cursor = self.database.conn.cursor()
        cursor.execute("""
            INSERT INTO tasks (subject_id, title, description, due_date, priority, is_completed)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            task.subject_id, 
            task.title, 
            task.description, 
            task.due_date.isoformat() if task.due_date else None, 
            task.priority, 
            1 if task.is_completed else 0
        ))
        self.database.conn.commit()
        return cursor.lastrowid

    def get_tasks_by_subject(self, subject_id: int) -> list[tuple]:
        cursor = self.database.conn.cursor()
        cursor.execute("""
            SELECT t.id, s.name, t.title, t.description, t.due_date, t.priority, t.is_completed
            FROM tasks t
            JOIN subjects s ON t.subject_id = s.id
            WHERE t.subject_id = ?
            ORDER BY t.priority DESC, t.due_date ASC
        """, (subject_id,))
        return cursor.fetchall()

    def get_all_tasks(self) -> list[tuple]:
        cursor = self.database.conn.cursor()
        cursor.execute("""
            SELECT t.id, s.name, t.title, t.description, t.due_date, t.priority, t.is_completed
            FROM tasks t
            JOIN subjects s ON t.subject_id = s.id
            ORDER BY t.is_completed ASC, t.priority DESC, t.due_date ASC
        """)
        return cursor.fetchall()

    def update_task_status(self, task_id: int, is_completed: bool):
        cursor = self.database.conn.cursor()
        cursor.execute("""
            UPDATE tasks SET is_completed = ? WHERE id = ?
        """, (1 if is_completed else 0, task_id))
        self.database.conn.commit()

    def delete_task(self, task_id: int):
        cursor = self.database.conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.database.conn.commit()

    def update_task(self, task_id: int, subject_id: int, title: str, description: str, due_date: date, priority: int):
        cursor = self.database.conn.cursor()
        cursor.execute("""
            UPDATE tasks 
            SET subject_id = ?, title = ?, description = ?, due_date = ?, priority = ?
            WHERE id = ?
        """, (
            subject_id, 
            title, 
            description, 
            due_date.isoformat() if due_date else None, 
            priority, 
            task_id
        ))
        self.database.conn.commit()

    def get_task_by_id(self, task_id: int) -> tuple:
        cursor = self.database.conn.cursor()
        cursor.execute("""
            SELECT t.id, s.name, t.title, t.description, t.due_date, t.priority, t.is_completed
            FROM tasks t
            JOIN subjects s ON t.subject_id = s.id
            WHERE t.id = ?
        """, (task_id,))
        return cursor.fetchone()

    def get_tasks_by_date(self, date_str: str) -> list[tuple]:
        cursor = self.database.conn.cursor()
        cursor.execute("""
            SELECT t.id, s.name, t.title, t.description, t.due_date, t.priority, t.is_completed
            FROM tasks t
            JOIN subjects s ON t.subject_id = s.id
            WHERE t.due_date = ?
            ORDER BY t.is_completed ASC, t.priority DESC
        """, (date_str,))
        return cursor.fetchall()
