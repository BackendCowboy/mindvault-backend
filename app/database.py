from sqlmodel import create_engine, SQLModel, Session
from app.config import DATABASE_URL, DEBUG
from app.logger import logger

# Create engine with proper configuration
if DATABASE_URL.startswith("postgresql"):
    # PostgreSQL configuration
    engine = create_engine(
        DATABASE_URL,
        echo=DEBUG,  # Only show SQL queries in debug mode
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=300,    # Recycle connections every 5 minutes
    )
else:
    # SQLite configuration (fallback for development)
    engine = create_engine(DATABASE_URL, echo=DEBUG)

def create_db_and_tables():
    """Create database tables"""
    from app.models import User, JournalEntry
    SQLModel.metadata.create_all(engine)

def get_session():
    """Get database session"""
    with Session(engine) as session:
        yield session

# Health check function
def check_db_connection():
    """Check if database connection is working"""
    try:
        with Session(engine) as session:
            session.exec("SELECT 1")
        return True
    except Exception as e:
        logger.info(f"Database connection failed: {e}")
        return False