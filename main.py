from fastapi import FastAPI, HTTPException
from sqlmodel import SQLModel, Field, Session, create_engine, select
from typing import List, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi import Depends, status

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        with Session(engine) as session:
            statement = select(User) .where (User.email == email)
            User = session.exec(statement).first()

            if not User:
                raise credentials_exception
        return User
    except JWTError:
        raise credentials_exception


app = FastAPI()

# SQLite database connection 
sqlite_file_name = "journal.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=True)

# password hashing

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def hash_password(password: str) -> str:
    return pwd_context.hash(password)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
def create_access_token( data: dict, expires_delta:Optional[timedelta]= None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Define the journal entry model (table)

class JournalEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str
    mood: str
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
# User Models
class User(SQLModel, table=True):
    id:Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str

class UserCreate(SQLModel):
    email: str
    password: str

class UserRead(SQLModel):
    id: int
    email: str


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

# POST: Add new journal entry 
@app.post("/journals")
def create_journal(entry: JournalEntry, user: dict = Depends(get_current_user)):
    with Session(engine) as session:
        entry.user_id = user.id
        session.add(entry)
        session.commit()
        session.refresh(entry)
        return {"message": "Entry saved", "entry": entry}
    

# GET: Get all journal entries 
@app.get("/journals", response_model=List[JournalEntry])
def get_journals(user: User = Depends(get_current_user)):
    with Session(engine) as session:
        statement = select(JournalEntry) .where(JournalEntry.user_id == user.id)
        results = session.exec(statement).all()
        return results
    

# DELETE: Delete a journal entry 

@app.delete("/journals/{entry_id}")
def delete_journal(entry_id: int, user: User = Depends(get_current_user)):
    with Session(engine) as session:
        entry = session.get(JournalEntry, entry_id)
        if not entry or entry.user_id != user.id:
            raise HTTPException(status_code=404, detail="Entry not found")

        session.delete(entry)
        session.commit()
        return {"message": f"Entry {entry_id} deleted"}




# PUT: Update journal entry by ID 

@app.put("/journals/{entry_id}")
def update_journal(entry_id: int, updated: JournalEntry, user: User = Depends(get_current_user)):
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
    
    # REGISTRATION ROUTE
@app.post("/register", response_model=UserRead)
def register(user: UserCreate):
    hashed = hash_password(user.password)
    db_user = User(email=user.email, hashed_password=hashed)

    with Session(engine) as session:
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user

# LOGIN ROUTE
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    with Session(engine) as session:
        statement = select(User).where(User.email == form_data.username)
        user = session.exec(statement).first()

        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        access_token = create_access_token(data={"sub": user.email})
        return {"access_token": access_token, "token_type": "bearer"}