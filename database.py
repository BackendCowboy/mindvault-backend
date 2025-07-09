# database.py
from sqlmodel import create_engine, SQLModel, Session

sqlite_file_name = "journal.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# ✅ Default engine for production
engine = create_engine(sqlite_url, echo=True)


def init_db():
    from models import User, JournalEntry
    SQLModel.metadata.create_all(engine)


# ✅ Make this accept an optional engine for test overrides
def get_session(db_engine=engine):
    def _get_session():
        with Session(db_engine) as session:
            yield session
    return _get_session()