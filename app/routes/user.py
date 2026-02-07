from fastapi import APIRouter, Depends
from app.database import get_db
from app.models import User
from app.schemas import UserResponse
from app.dependencies.auth import get_current_user
from sqlalchemy.orm import Session

router = APIRouter(prefix="/user", tags=["User"])

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/profile")
def get_profile(current_user: User = Depends(get_current_user)):
    return {
        "message": f"Welcome, {current_user.name}!",
        "user_id": current_user.id,
        "email_verified": current_user.email_verified
    }


@router.put("/profile")
def update_profile(
    name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    current_user.name = name
    db.commit()
    db.refresh(current_user)
    
    return {
        "message": "Profile updated",
        "user": {
            "id": current_user.id,
            "name": current_user.name
        }
    }
