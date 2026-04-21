from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, verify_password
import logging

logger = logging.getLogger(__name__)


class UserCRUD:
    """Class-based CRUD operations for User"""
    
    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        try:
            return db.query(User).filter(User.username == username).first()
        except SQLAlchemyError as e:
            logger.error(f"Database error while fetching user: {str(e)}")
            raise
    
    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            return db.query(User).filter(User.email == email).first()
        except SQLAlchemyError as e:
            logger.error(f"Database error while fetching user: {str(e)}")
            raise
    
    @staticmethod
    def create(db: Session, user_data: UserCreate) -> User:
        """Create a new user"""
        try:
            logger.info(f"Creating user: {user_data.username}")
            
            # Check if username exists
            if UserCRUD.get_by_username(db, user_data.username):
                raise ValueError("Username already exists")
            
            # Check if email exists
            if UserCRUD.get_by_email(db, user_data.email):
                raise ValueError("Email already exists")
            
            hashed_password = get_password_hash(user_data.password)
            
            new_user = User(
                username=user_data.username,
                email=user_data.email,
                hashed_password=hashed_password,
                full_name=user_data.full_name,
                role=user_data.role,
                is_active=True
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            logger.info(f"User created successfully: {new_user.username}")
            return new_user
            
        except ValueError:
            raise
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error while creating user: {str(e)}")
            raise
    
    @staticmethod
    def authenticate(db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        try:
            user = UserCRUD.get_by_email(db, email)
            if not user:
                return None
            if not verify_password(password, user.hashed_password):
                return None
            return user
        except SQLAlchemyError as e:
            logger.error(f"Database error while authenticating user: {str(e)}")
            raise


# Create instance for backward compatibility
user_crud = UserCRUD()