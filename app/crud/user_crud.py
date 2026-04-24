from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, verify_password
from app.enums.user_enums import UserRole
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
    def get_by_oauth_subject(db: Session, provider: str, subject: str) -> Optional[User]:
        """Get user by OAuth provider and subject"""
        try:
            return (
                db.query(User)
                .filter(User.oauth_provider == provider, User.oauth_subject == subject)
                .first()
            )
        except SQLAlchemyError as e:
            logger.error(f"Database error while fetching OAuth user: {str(e)}")
            raise

    @staticmethod
    def _generate_unique_username(db: Session, base_username: str) -> str:
        """Generate a unique username for OAuth-created users"""
        username = "".join(ch for ch in base_username if ch.isalnum() or ch in {"_", "."}).strip("._")
        username = username or "user"
        candidate = username[:50]
        suffix = 1

        while UserCRUD.get_by_username(db, candidate):
            suffix_str = str(suffix)
            candidate = f"{username[: max(1, 50 - len(suffix_str) - 1)]}_{suffix_str}"
            suffix += 1

        return candidate
    
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
            if not user.hashed_password:
                return None
            if not verify_password(password, user.hashed_password):
                return None
            return user
        except SQLAlchemyError as e:
            logger.error(f"Database error while authenticating user: {str(e)}")
            raise

    @staticmethod
    def get_or_create_google_user(
        db: Session,
        *,
        email: str,
        subject: str,
        full_name: Optional[str],
        role: UserRole
    ) -> User:
        """Link or create a local user for a Google account"""
        try:
            oauth_user = UserCRUD.get_by_oauth_subject(db, "google", subject)
            if oauth_user:
                oauth_user.email = email
                oauth_user.full_name = full_name or oauth_user.full_name
                oauth_user.is_active = True
                db.commit()
                db.refresh(oauth_user)
                return oauth_user

            existing_user = UserCRUD.get_by_email(db, email)
            if existing_user:
                existing_user.oauth_provider = "google"
                existing_user.oauth_subject = subject
                existing_user.full_name = full_name or existing_user.full_name
                existing_user.is_active = True
                db.commit()
                db.refresh(existing_user)
                return existing_user

            base_username = email.split("@", 1)[0]
            username = UserCRUD._generate_unique_username(db, base_username)

            new_user = User(
                username=username,
                email=email,
                hashed_password=None,
                full_name=full_name,
                role=role,
                oauth_provider="google",
                oauth_subject=subject,
                is_active=True
            )

            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            return new_user
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error while processing Google user: {str(e)}")
            raise


# Create instance for backward compatibility
user_crud = UserCRUD()
