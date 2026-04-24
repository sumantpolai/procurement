import uuid
from sqlalchemy import Column, String, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from app.database.db import Base
from app.enums.user_enums import UserRole
from app.core.timezone import get_current_time


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    role = Column(SQLEnum(UserRole), nullable=False)
    oauth_provider = Column(String, nullable=True, index=True)
    oauth_subject = Column(String, unique=True, nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    google_id = Column(String, unique=True, nullable=True, index=True)  # For Google OAuth
    oauth_provider = Column(String, nullable=True)  # 'google', 'github', etc.
    created_at = Column(DateTime, default=lambda: get_current_time().replace(tzinfo=None), nullable=False)
    updated_at = Column(DateTime, default=lambda: get_current_time().replace(tzinfo=None), onupdate=lambda: get_current_time().replace(tzinfo=None))
