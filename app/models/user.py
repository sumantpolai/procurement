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
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(SQLEnum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: get_current_time().replace(tzinfo=None), nullable=False)
    updated_at = Column(DateTime, default=lambda: get_current_time().replace(tzinfo=None), onupdate=lambda: get_current_time().replace(tzinfo=None))
