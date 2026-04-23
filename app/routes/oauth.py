from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request
from datetime import timedelta
import httpx

from app.database.db import get_db
from app.models.user import User
from app.enums.user_enums import UserRole
from app.core.config import settings
from app.core.security import create_access_token
from app.core.logger import setup_logger
from app.core.timezone import get_current_time

router = APIRouter(prefix="/auth/google", tags=["OAuth - Google"])
logger = setup_logger(__name__)

# Configure OAuth
oauth = OAuth()
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)


@router.get(
    "/login",
    summary="Login with Google",
    description="Redirect to Google OAuth login page"
)
async def google_login(request: Request):
    """
    Initiate Google OAuth login
    
    Redirects user to Google's OAuth consent screen
    """
    try:
        redirect_uri = settings.GOOGLE_REDIRECT_URI
        return await oauth.google.authorize_redirect(request, redirect_uri)
    except Exception as e:
        logger.error(f"Google OAuth login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate Google login"
        )


@router.get(
    "/callback",
    summary="Google OAuth Callback",
    description="Handle Google OAuth callback and create/login user"
)
async def google_callback(request: Request, db: Session = Depends(get_db)):
    """
    Handle Google OAuth callback
    
    - Creates new user if doesn't exist
    - Logs in existing user
    - Returns JWT token
    """
    try:
        current_time = get_current_time()
        
        # Get token from Google
        token = await oauth.google.authorize_access_token(request)
        
        # Get user info from Google
        user_info = token.get('userinfo')
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user info from Google"
            )
        
        google_id = user_info.get('sub')
        email = user_info.get('email')
        full_name = user_info.get('name')
        
        if not email or not google_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email or Google ID not provided by Google"
            )
        
        logger.info(f"[{current_time}] Google OAuth: User {email} attempting login")
        
        # Check if user exists by google_id
        user = db.query(User).filter(User.google_id == google_id).first()
        
        # If not found by google_id, check by email
        if not user:
            user = db.query(User).filter(User.email == email).first()
            
            # If user exists with email but no google_id, link the account
            if user:
                user.google_id = google_id
                user.oauth_provider = 'google'
                db.commit()
                db.refresh(user)
                logger.info(f"[{current_time}] Linked existing user {email} with Google account")
        
        # Create new user if doesn't exist
        if not user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "USER_NOT_REGISTERED",
                    "message": "No account found with this email. Please register first with email/password and specify your role, then you can link your Google account.",
                    "email": email,
                    "google_id": google_id
                }
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email, "role": user.role.value, "user_id": str(user.id)},
            expires_delta=access_token_expires
        )
        
        logger.info(f"[{current_time}] User logged in via Google: {email}")
        
        # Return token as JSON response
        # In production, you might want to redirect to frontend with token
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value,
                "oauth_provider": user.oauth_provider
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google OAuth callback error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth callback failed: {str(e)}"
        )
