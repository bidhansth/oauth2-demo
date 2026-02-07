from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from app.config import settings

def create_access_token(user_id: int, expires_delta: Optional[timedelta]= None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )

    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access"
    }

    encoded_jwt = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def verify_access_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        if payload.get("type") != "access":
            raise JWTError("Invalid token type")
        
        return payload
    except JWTError as e:
        raise JWTError(f"Invalid token: {str(e)}")
    
    
def get_user_id_from_token(token: str) -> Optional[int]:
    try:
        payload = verify_access_token(token)
        user_id = payload.get("sub")
        
        if user_id is None:
            return None
        
        return int(user_id)
        
    except (JWTError, ValueError):
        return None
    