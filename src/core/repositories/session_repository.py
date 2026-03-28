from datetime import datetime, date
from core.database import Database
from core.models import StudySession

class SessionRepository:
    def __init__(self, database: Database):
        self.database = database

    def add_entry(self, session: StudySession) -> int:
        cursor = self.database.conn.cursor()
        cursor.execute("""
            INSERT INTO study_sessions (subject_id, date, start_time, end_time, quality, notes) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            session.subject_id, 
            session.date.isoformat(), 
            session.start_time.isoformat(), 
            session.end_time.isoformat(), 
            session.quality, 
            session.notes
        ))
        self.database.conn.commit()
        return cursor.lastrowid

    def get_last_entries(self, limit=10) -> list[tuple]:
        cursor = self.database.conn.cursor()
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

    def modify_entry(self, entry_id: int, subject_id: int, entry_date: date, start_time: datetime, end_time: datetime, notes: str, quality: int):
        cursor = self.database.conn.cursor()
        cursor.execute("""
            UPDATE study_sessions 
            SET subject_id = ?, date = ?, start_time = ?, end_time = ?, notes = ?, quality = ?
            WHERE id = ?
        """, (
            subject_id, 
            entry_date.isoformat(), 
            start_time.isoformat(), 
            end_time.isoformat(), 
            notes, 
            quality, 
            entry_id
        ))
        self.database.conn.commit()

    def delete_entry(self, entry_id: int):
        cursor = self.database.conn.cursor()
        cursor.execute("DELETE FROM study_sessions WHERE id = ?", (entry_id,))
        self.database.conn.commit()

    def get_entry_by_id(self, entry_id: int) -> StudySession | None:
        cursor = self.database.conn.cursor()
        cursor.execute("""
            SELECT id, subject_id, date, start_time, end_time, quality, notes
            FROM study_sessions WHERE id = ?
        """, (entry_id,))
        row = cursor.fetchone()
        if not row:
            return None
            
        # Converting back to Value Objects
        return StudySession(
            id=row[0],
            subject_id=row[1],
            date=date.fromisoformat(row[2]),
            start_time=datetime.fromisoformat(row[3]),
            end_time=datetime.fromisoformat(row[4]),
            quality=row[5],
            notes=row[6]
        )

    def get_entries_by_date(self, date_str: str) -> list[tuple]:
        cursor = self.database.conn.cursor()
        cursor.execute("""
            SELECT ss.id, s.name, ss.start_time, ss.end_time, ss.quality, ss.notes
            FROM study_sessions ss
            JOIN subjects s ON ss.subject_id = s.id
            WHERE ss.date = ?
            ORDER BY ss.start_time ASC
        """, (date_str,))
        return cursor.fetchall()

    def get_daily_stats(self, days=365):
        cursor = self.database.conn.cursor()
        cursor.execute("""
            SELECT date, SUM(duration_hours)
            FROM study_sessions
            WHERE date >= date('now', ?)
            GROUP BY date
            ORDER BY date ASC
        """, (f"-{days} days",))
        return cursor.fetchall()
