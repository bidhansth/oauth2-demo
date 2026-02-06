from sqlalchemy import String, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from typing import List
from app.database import Base

class User(Base):
    __tablename__ = "users"

    # id = Column(Integer, primary_key=True, index=True)
    # email = Column(String, unique=True, nullable=True, index=True)
    # email_verified = Column(Boolean, default=False)
    # name = Column(String, nullable=True)
    # avatar_url = Column(String, nullable=True)
    # is_active = Column(Boolean, default=True)
    # created_at = Column(DateTime, default=datetime.now(timezone.utc))
    # updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str | None] = mapped_column(String, unique=True, nullable=True, index=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    # oauth_identities = relationship("OAuthIdentity", back_populates="user", cascade="all, delete-orphan")
    oauth_identities: Mapped[List["OAuthIdentity"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"
    
class OAuthIdentity(Base):
    __tablename__ = "oauth_identities"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String, nullable=False, index=True)
    provider_sub: Mapped[str] = mapped_column(String, nullable=False, index=True)
    provider_email: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user: Mapped["User"] = relationship(back_populates="oauth_identities")
    
    __table_args__ = (
        UniqueConstraint("provider", "provider_sub", name="uq_provider_identity"),
    )
    
    def __repr__(self):
        return f"<OAuthIdentity(provider={self.provider}, sub={self.provider_sub})>"