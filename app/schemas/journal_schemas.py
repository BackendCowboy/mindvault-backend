from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class JournalEntryCreate(BaseModel):
    title: str
    content: str
    mood: str


class JournalEntryUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    mood: Optional[str] = None
    reflection: Optional[str] = None  # 🧠 new optional field


class JournalEntryResponse(BaseModel):
    id: int
    title: str
    content: str
    mood: str
    reflection: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
