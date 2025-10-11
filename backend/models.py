# backend/models.py
from typing import Optional
from sqlmodel import SQLModel, Field, create_engine, Session, select
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    role: str = "student"  # admin/instructor/student
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Progress(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    topic: str
    completed_percent: float = 0.0
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class QuizResult(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    topic: str
    score: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
