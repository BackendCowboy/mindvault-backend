# database.py
from sqlmodel import create_engine, SQLModel

sqlite_file_name = "journal.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)

def init_db():
    from models import User, JournalEntry
    SQLModel.metadata.create_all(engine)