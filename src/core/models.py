from dataclasses import dataclass
from datetime import date, datetime

@dataclass
class StudySession:
    id: int | None
    subject_id: int
    date: date
    start_time: datetime
    end_time: datetime
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
    due_date: date | None = None
    priority: int = 2  # 1: Low, 2: Medium, 3: High
    is_completed: bool = False

@dataclass
class SubjectDetails:
    id: int
    name: str
    semester: int
    year: int
    credits: int
    notes: str
    total_hours: float
    avg_quality: float
