from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from app.config import settings
from app.routes import auth, user

app = FastAPI()
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.JWT_SECRET_KEY,
    session_cookie="session",
    max_age=1800,
    same_site="lax",
    https_only=False,
    # path="/"
)
app.include_router(auth.router)
app.include_router(user.router)

@app.get("/")
def root():
    return {"message":"Hello"}
