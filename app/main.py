from fastapi import FastAPI, Depends
from sqlalchemy import select
from app.config import settings
from sqlalchemy.orm import Session
from app.database import get_db, create_tables
from app.models import User, OAuthIdentity
from app.schemas import UserResponse
from app.oauth.client import oauth

app = FastAPI()

@app.get("/")
def root():
    return {"message":"Hello"}

@app.post("/debug/create-test-user", response_model=UserResponse)
def debug_create_user(db: Session = Depends(get_db)):
    stmt = select(User).where(User.email == "test@example.com")
    existing = db.execute(stmt).scalar_one_or_none()
    if existing:
        return existing
    
    test_user = User(
        email="test@example.com",
        email_verified=True,
        name="Test User",
        avatar_url=None,
        is_active=True
    )

    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    return test_user

@app.get("/debug/oauth-config")
def debug_oauth_config():
    google_client = oauth.create_client("google")
    
    return {
        "provider": "google",
        "has_client_id": bool(settings.GOOGLE_CLIENT_ID),
        "has_client_secret": bool(settings.GOOGLE_CLIENT_SECRET),
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "client_configured": google_client is not None,
    }