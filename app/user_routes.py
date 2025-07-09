# app/user_routes.py

from fastapi import APIRouter, Depends
from app.auth import get_current_user
from app.models import UserRead

router = APIRouter()

@router.get("/me", response_model=UserRead)
def get_me(user=Depends(get_current_user)):
    return user