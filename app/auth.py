# app/auth.py
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from sqlmodel import Session, select
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.models import User, UserCreate
from app.database import engine

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ← this must match your login path exactly:
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
print(f"OAuth2PasswordBearer configured with tokenUrl: /auth/login")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    print(f"get_current_user called with token: {token[:20] if token else 'None'}...")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Decoded payload: {payload}") 
        email: str = payload.get("sub")
        if not email:
            raise credentials_exception
        with Session(engine) as session:
            user = session.exec(select(User).where(User.email == email)).first()
            print(f"Found user: {user.email if user else 'None'}")  
            if not user:
                raise credentials_exception
            return user
    except JWTError as e:
        print(f"JWT Error: {e}")  
        raise credentials_exception

def register_user(user_data: UserCreate):
    with Session(engine) as session:
        hashed = hash_password(user_data.password)
        db_user = User(email=user_data.email, hashed_password=hashed)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user

def authenticate_user(email: str, password: str):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user