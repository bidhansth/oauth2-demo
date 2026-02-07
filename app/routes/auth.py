from fastapi import APIRouter, Request, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.oauth.client import oauth
from app.config import settings
from app.database import get_db
from app.services.auth_service import upsert_oauth_user
from app.security.jwt import create_access_token, verify_access_token, get_user_id_from_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.get("/login")
async def login(request: Request):
    request.session.clear()
    
    google = oauth.create_client("google")
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    
    return await google.authorize_redirect(request, redirect_uri)


@router.get("/callback")
async def callback(request: Request, db: Session = Depends(get_db)):
    if "error" in request.query_params:
        error = request.query_params.get("error")
        error_description = request.query_params.get("error_description", "User denied access")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"OAuth error: {error} - {error_description}"
        )
    
    google = oauth.create_client("google")
    
    try:
        token = await google.authorize_access_token(request)
    except Exception as e:
        request.session.clear()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Authentication failed: {str(e)}"
        )
    
    user_info = token.get("userinfo")
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No user info in token response"
        )
    
    claims = {
        "sub": user_info.get("sub"),
        "email": user_info.get("email"),
        "email_verified": user_info.get("email_verified", False),
        "name": user_info.get("name"),
        "picture": user_info.get("picture"),
    }
    
    if not claims["sub"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing subject claim in ID token"
        )
    
    try:
        user = upsert_oauth_user(db, provider="google", user_claims=claims)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save user: {str(e)}"
        )

    request.session.clear()
    access_token = create_access_token(user_id=user.id)
    
    return JSONResponse(
        content={
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name
            }
        }
    )


@router.post("/logout")
async def logout(request: Request):
    request.session.clear()

    return JSONResponse(
        content={
            "message": "Logged out successfully",
            "note": "Client should delete the access token"
        }
    )
