from fastapi import FastAPI, HTTPException
from sqlmodel import SQLModel, Field, Session, create_engine, select
from typing import List, Optional
from datetime import datetime

app = FastAPI()

# SQLite database connection 
sqlite_file_name = "journal.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=True)

# Define the journal entry model (table)

class JournalEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str
    mood: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Create table 

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

# POST: Add new journal entry 
@app.post("/journals")
def create_journal(entry: JournalEntry):
    with Session(engine) as session:
        session.add(entry)
        session.commit()
        session.refresh(entry)
        return {"message": "Entry saved", "entry": entry}
    

# GET: Get all journal entries 
@app.get("/journals", response_model=List[JournalEntry])
def get_journals():
    with Session(engine) as session:
        statement = select(JournalEntry)
        results = session.exec(statement).all()
        return results
    

# DELETE: Delete a journal entry 

@app.delete("/journals/{entry_id}")
def delete_journal(entry_id: int):
    with Session(engine) as session:
        entry = session.get(JournalEntry, entry_id)
        if not entry:
            raise HTTPException(status_code=404, detail="Entry not found")

        session.delete(entry)
        session.commit()
        return {"message": f"Entry {entry_id} deleted"}




# PUT: Update journal entry by ID 

@app.put("/journals/{entry_id}")
def update_journal(entry_id: int, updated: JournalEntry):
    with Session(engine) as session:
        entry = session.get(JournalEntry, entry_id)
        if not entry:
            raise HTTPException(status_code=404, detail="Entry not found")

        entry.title = updated.title
        entry.content = updated.content
        entry.mood = updated.mood
        entry.updated_at = datetime.utcnow()

        session.add(entry)
        session.commit()
        session.refresh(entry)
        return {"message": f"Entry {entry_id} updated", "entry": entry}