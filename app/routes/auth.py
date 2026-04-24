from urllib.error import HTTPError, URLError

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database.db import get_db
from app.schemas.user import UserCreate, UserResponse, Token, UserLogin, GoogleAuthURLResponse
from app.crud.user_crud import UserCRUD
from app.core.security import create_access_token
from app.core.config import settings
from app.core.logger import setup_logger
from app.core.timezone import get_current_time
from app.core.dependencies import get_current_user
from app.models.user import User
from app.enums.user_enums import UserRole
from app.services.google_oauth import (
    build_google_authorization_url,
    create_google_oauth_state,
    exchange_code_for_tokens,
    verify_google_identity_token,
    verify_google_oauth_state,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = setup_logger(__name__)


def _create_token_response(user: User) -> dict:
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.value, "user_id": str(user.id)},
        expires_delta=access_token_expires
    )
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

        logger.info(f"[{current_time}] API: User logged in successfully: {user.email}")
        return _create_token_response(user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Login error - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "LOGIN_ERROR", "message": "Failed to login"}
        )


@router.get(
    "/google/url",
    response_model=GoogleAuthURLResponse,
    summary="Get Google OAuth2 Authorization URL",
    description="Create the Google OAuth2 authorization URL used to start the login flow"
)
async def get_google_auth_url():
    """Return the Google authorization URL so the frontend can redirect the user."""
    state = create_google_oauth_state()
    return {
        "authorization_url": build_google_authorization_url(state),
        "state": state,
    }


@router.get(
    "/google/login",
    summary="Redirect to Google Login",
    description="Redirect the browser to Google to begin the OAuth2 login flow"
)
async def google_login():
    """Redirect the user to the Google authorization page."""
    state = create_google_oauth_state()
    authorization_url = build_google_authorization_url(state)
    return RedirectResponse(url=authorization_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@router.get(
    "/google/callback",
    response_model=Token,
    summary="Google OAuth2 Callback",
    description="Handle the Google OAuth2 callback, create or link the local user, and return an app access token"
)
async def google_callback(
    code: str = Query(..., description="Google authorization code"),
    state: str = Query(..., description="OAuth2 state token"),
    db: Session = Depends(get_db)
):
    """Complete the Google OAuth2 login flow and issue the app JWT."""
    try:
        verify_google_oauth_state(state)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "INVALID_OAUTH_STATE", "message": str(e)}
        ) from e

    try:
        token_payload = exchange_code_for_tokens(code)
    except HTTPError as e:
        logger.error(f"Google token exchange failed: {e.reason}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"error": "GOOGLE_TOKEN_EXCHANGE_FAILED", "message": "Failed to exchange code with Google"}
        ) from e
    except URLError as e:
        logger.error(f"Google token exchange network error: {e.reason}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"error": "GOOGLE_NETWORK_ERROR", "message": "Could not reach Google OAuth service"}
        ) from e

    id_token = token_payload.get("id_token")
    if not id_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "MISSING_ID_TOKEN", "message": "Google response did not include an ID token"}
        )

    try:
        google_user = verify_google_identity_token(id_token)
        role = UserRole(settings.GOOGLE_OAUTH_DEFAULT_ROLE)
        user = UserCRUD.get_or_create_google_user(
            db,
            email=google_user["email"],
            subject=google_user["sub"],
            full_name=google_user.get("name"),
            role=role,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "GOOGLE_IDENTITY_ERROR", "message": str(e)}
        ) from e
    except Exception as e:
        logger.error(f"Google login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "GOOGLE_LOGIN_FAILED", "message": "Failed to complete Google login"}
        ) from e

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    return _create_token_response(user)


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
