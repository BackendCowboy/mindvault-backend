# app/schemas.py
from pydantic import BaseModel

class JournalEntryCreate(BaseModel):
    title: str
    content: str
    mood: str