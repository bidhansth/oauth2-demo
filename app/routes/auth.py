from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import JSONResponse
from app.oauth.client import oauth
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.get("/login")
async def login(request: Request):
    google = oauth.create_client("google")
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    
    return await google.authorize_redirect(request, redirect_uri)

@router.get("/callback")
async def callback(request: Request):
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
        "provider": "google"
    }

    if not claims["sub"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing subject claim in ID token"
        )
    
    return JSONResponse(
        content={
            "message": "OAuth login successful!",
            "user": claims
        }
    )
