from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import User, OAuthIdentity
from typing import Dict, Any

def upsert_oauth_user(
        db: Session,
        provider: str,
        user_claims: Dict[str,Any]
) -> User:
    provider_sub = user_claims.get("sub")
    if not provider_sub:
        raise ValueError("Missing 'sub' claim - cannot identify user")
    
    stmt = select(OAuthIdentity).where(
        OAuthIdentity.provider == provider,
        OAuthIdentity.provider_sub == provider_sub
    )
    oauth_identity = db.execute(stmt).scalar_one_or_none()

    if oauth_identity:
        user = oauth_identity.user
        if user_claims.get("email"):
            user.email = user_claims["email"]
        if user_claims.get("email_verified") is not None:
            user.email_verified = user_claims["email_verified"]
        if user_claims.get("name"):
            user.name = user_claims["name"]
        if user_claims.get("picture"):
            user.avatar_url = user_claims["picture"]

        oauth_identity.provider_email = user_claims.get("email")

        db.commit()
        db.refresh(user)

        return user
    else:
        new_user = User(
            email=user_claims.get("email"),
            email_verified=user_claims.get("email_verified", False),
            name=user_claims.get("name"),
            avatar_url=user_claims.get("picture"),
            is_active=True
        )
        db.add(new_user)
        db.flush()

        new_identity = OAuthIdentity(
            user_id=new_user.id,
            provider=provider,
            provider_sub=provider_sub,
            provider_email=user_claims.get("email")
        )
        db.add(new_identity)
        db.commit()
        db.refresh(new_user)

        return new_user
    