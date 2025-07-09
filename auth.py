# auth.py
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
from sqlmodel import Session, select
from fastapi import HTTPException, status, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from models import User, UserCreate

from database import engine

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = HTTPBearer()

# --- PASSWORD UTILS ---
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# --- TOKEN UTILS ---
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# --- GET CURRENT USER ---
def get_current_user(credentials: HTTPAuthorizationCredentials = Security(oauth2_scheme)):
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        with Session(engine) as session:
            user = session.exec(select(User).where(User.email == email)).first()
            if not user:
                raise credentials_exception
            return user
    except JWTError:
        raise credentials_exception

# --- REGISTER USER ---
def register_user(user_data: UserCreate):
    with Session(engine) as session:
        hashed = hash_password(user_data.password)
        db_user = User(email=user_data.email, hashed_password=hashed)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user

# --- AUTHENTICATE USER ---
def authenticate_user(email: str, password: str):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user