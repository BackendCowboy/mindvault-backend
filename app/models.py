# models.py
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str
    hashed_password: str

class JournalEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str
    mood: str
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(SQLModel):
    email: str
    password: str

class UserRead(SQLModel):
    id: int
    email: str

class JournalEntryUpdate(SQLModel):
    title: Optional[str] = None
    content: Optional[str] = None
    mood: Optional[str] = None
    updated_at: Optional[datetime] = None