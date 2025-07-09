from sqlmodel import create_engine, SQLModel, Session

sqlite_file_name = "journal.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)


# 🔁 Rename to match import
def create_db_and_tables():
    from app.models import User, JournalEntry
    SQLModel.metadata.create_all(engine)


def get_session(db_engine=engine):
    def _get_session():
        with Session(db_engine) as session:
            yield session
    return _get_session()