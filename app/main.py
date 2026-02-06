from fastapi import FastAPI, Depends
from sqlalchemy import select
from app.config import settings
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import UserResponse
from app.oauth.client import oauth
from app.routes import auth
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request

app = FastAPI()
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.JWT_SECRET_KEY,
    session_cookie="session",
    max_age=1800,
    same_site="lax",
    https_only=False
)
app.include_router(auth.router)

@app.get("/")
def root():
    return {"message":"Hello"}

@app.get("/debug/session")
async def debug_session(request: Request):
    """Debug endpoint to check session."""
    from starlette.requests import Request as StarletteRequest
    return {
        "session_contents": dict(request.session),
        "cookies": dict(request.cookies)
    }

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
