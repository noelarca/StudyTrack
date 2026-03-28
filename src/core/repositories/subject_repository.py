from core.database import Database
from core.models import Subject, SubjectDetails

class SubjectRepository:
    def __init__(self, database: Database):
        self.database = database

    def add_subject(self, subject: Subject) -> int:
        cursor = self.database.conn.cursor()
        cursor.execute("""
            INSERT INTO subjects (name, semester, year, credits, notes) VALUES (?, ?, ?, ?, ?)
        """, (subject.name, subject.semester, subject.year, subject.credits, subject.notes))
        self.database.conn.commit()
        return cursor.lastrowid

    def get_subject_id_by_name(self, name: str) -> int | None:
        cursor = self.database.conn.cursor()
        cursor.execute("SELECT id FROM subjects WHERE name = ?", (name,))
        result = cursor.fetchone()
        return result[0] if result else None

    def get_all_subjects(self) -> list[Subject]:
        cursor = self.database.conn.cursor()
        cursor.execute("SELECT id, name, semester, year, credits, notes FROM subjects")
        rows = cursor.fetchall()
        return [Subject(*row) for row in rows]

    def get_subject_by_name(self, name: str) -> Subject | None:
        cursor = self.database.conn.cursor()
        cursor.execute(
            "SELECT id, name, semester, year, credits, notes "
            "FROM subjects WHERE name = ?", (name,))
        row = cursor.fetchone()
        return Subject(*row) if row else None

    def get_subject_minor_stats(self, name: str):
        cursor = self.database.conn.cursor()
        cursor.execute("""
            SELECT 
                IFNULL(SUM((julianday(end_time) - julianday(start_time)) * 24.0), 0) AS total_hours,
                IFNULL(AVG(quality), 0) AS avg_quality
            FROM study_sessions ss
            JOIN subjects s ON ss.subject_id = s.id
            WHERE s.name = ?
        """, (name,))
        return cursor.fetchone()

    def get_subject_details(self, name: str) -> SubjectDetails | None:
        subject = self.get_subject_by_name(name)
        if not subject:
            return None
        stats = self.get_subject_minor_stats(name)
        return SubjectDetails(
            id=subject.id,
            name=subject.name,
            semester=subject.semester,
            year=subject.year,
            credits=subject.credits,
            notes=subject.notes,
            total_hours=stats[0],
            avg_quality=stats[1]
        )

    def modify_subject(self, subject_id: int, name: str, semester: int, year: int, credits: int, notes: str):
        cursor = self.database.conn.cursor()
        cursor.execute("""
            UPDATE subjects 
            SET name = ?, semester = ?, year = ?, credits = ?, notes = ?
            WHERE id = ?
        """, (name, semester, year, credits, notes, subject_id))
        self.database.conn.commit()

    def delete_subject(self, subject_id: int):
        cursor = self.database.conn.cursor()
        cursor.execute("DELETE FROM study_sessions WHERE subject_id = ?", (subject_id,))
        cursor.execute("DELETE FROM tasks WHERE subject_id = ?", (subject_id,))
        cursor.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
        self.database.conn.commit()

    def get_subject_streak(self, name: str) -> int:
        cursor = self.database.conn.cursor()
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
        if dates[0] < today - timedelta(days=1):
            return 0
            
        if dates[0] == today:
            streak = 1
            current_check = today - timedelta(days=1)
        elif dates[0] == today - timedelta(days=1):
            streak = 1
            current_check = today - timedelta(days=2)
        else:
            return 0
            
        for i in range(1 if dates[0] >= today - timedelta(days=1) else 0, len(dates)):
            if dates[i] == current_check:
                streak += 1
                current_check -= timedelta(days=1)
            elif dates[i] > current_check:
                continue
            else:
                break
                
        return streak

    def get_subject_quality_distribution(self, name: str):
        cursor = self.database.conn.cursor()
        cursor.execute("""
            SELECT ss.quality, COUNT(*)
            FROM study_sessions ss
            JOIN subjects s ON ss.subject_id = s.id
            WHERE s.name = ?
            GROUP BY ss.quality
        """, (name,))
        return dict(cursor.fetchall())

    def get_subject_stats_over_time(self, name: str, days=7):
        cursor = self.database.conn.cursor()
        cursor.execute("""
            SELECT ss.date, SUM(ss.duration_hours)
            FROM study_sessions ss
            JOIN subjects s ON ss.subject_id = s.id
            WHERE s.name = ? AND ss.date >= date('now', ?)
            GROUP BY ss.date
            ORDER BY ss.date ASC
        """, (name, f"-{days} days"))
        return cursor.fetchall()
