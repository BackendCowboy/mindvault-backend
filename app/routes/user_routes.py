# app/user_routes.py
from fastapi import APIRouter, Depends
from app.auth import get_current_user
from app.models import UserRead

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserRead)
def read_me(current_user = Depends(get_current_user)):
    return current_user