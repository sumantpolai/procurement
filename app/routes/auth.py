from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database.db import get_db
from app.schemas.user import UserCreate, UserResponse, Token, UserLogin
from app.crud.user_crud import UserCRUD
from app.core.security import create_access_token
from app.core.config import settings
from app.core.logger import setup_logger
from app.core.timezone import get_current_time
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = setup_logger(__name__)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register New User",
    description="Register a new user with username, email, password, and role"
)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user
    
    - **username**: Unique username (min 3 chars)
    - **email**: Valid email address
    - **password**: Password (min 6 chars)
    - **role**: User role (store_staff, store_manager, purchase_staff, purchase_manager)
    """
    try:
        current_time = get_current_time()
        logger.info(f"[{current_time}] API: Register request received for username: {user_data.username}")
        user = UserCRUD.create(db, user_data)
        logger.info(f"[{current_time}] API: User registered successfully: {user.username}")
        return user
    except ValueError as e:
        logger.warning(f"API: Registration failed - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "REGISTRATION_FAILED", "message": str(e)}
        )
    except Exception as e:
        logger.error(f"API: Failed to register user - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "DATABASE_ERROR", "message": "Failed to register user"}
        )


@router.post(
    "/login",
    response_model=Token,
    summary="Login with Email and Password",
    description="Login with email and password to get access token"
)
async def login(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login to get access token
    
    - **email**: Your email address
    - **password**: Your password
    """
    try:
        current_time = get_current_time()
        logger.info(f"[{current_time}] API: Login request received for email: {user_data.email}")
        
        user = UserCRUD.authenticate(db, user_data.email, user_data.password)
        
        if not user:
            logger.warning(f"API: Login failed for email: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            logger.warning(f"API: Inactive user attempted login: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email, "role": user.role.value, "user_id": str(user.id)},
            expires_delta=access_token_expires
        )
        
        logger.info(f"[{current_time}] API: User logged in successfully: {user.email}")
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Login error - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "LOGIN_ERROR", "message": "Failed to login"}
        )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get Current User",
    description="Get the currently authenticated user's information"
)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information
    
    Returns user details including role
    """
    return current_user
