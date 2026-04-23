# Google OAuth Implementation - Line by Line Code Summary

## Table of Contents
1. [Overview](#overview)
2. [File Structure](#file-structure)
3. [Code Breakdown](#code-breakdown)
4. [Flow Diagram](#flow-diagram)
5. [Security Features](#security-features)

---

## Overview

This document explains the Google OAuth 2.0 implementation in the Procurement Management System. OAuth allows users to login using their Google account instead of creating a password.

**Key Requirement:** Users MUST register first with email/password to choose their role. Google login only works for existing users.

---

## File Structure

```
procurement/
├── app/
│   ├── routes/
│   │   ├── oauth.py          # NEW: OAuth endpoints
│   │   └── auth.py           # Existing: Email/password auth
│   ├── models/
│   │   └── user.py           # MODIFIED: Added OAuth fields
│   ├── core/
│   │   ├── config.py         # MODIFIED: Added OAuth settings
│   │   └── security.py       # Existing: JWT token creation
│   └── main.py               # MODIFIED: Added SessionMiddleware
├── .env                      # MODIFIED: Added Google credentials
├── requirements.txt          # MODIFIED: Added OAuth dependencies
└── migrate_oauth.py          # NEW: Database migration script
```

---

## Code Breakdown

### 1. `app/routes/oauth.py` - OAuth Routes (NEW FILE)

#### Line 1-11: Imports
```python
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
```

**Explanation:**
- `APIRouter` - Creates API endpoints
- `OAuth` - Main OAuth 2.0 client from authlib library
- `Request` - Needed to access session data
- `Session` - Database connection
- `User` - User database model
- `UserRole` - Enum for user roles

#### Line 12-15: Setup
```python
from app.core.config import settings
from app.core.security import create_access_token
from app.core.logger import setup_logger
from app.core.timezone import get_current_time
```

**Explanation:**
- `settings` - Access environment variables (Google credentials)
- `create_access_token` - Generate JWT tokens
- `setup_logger` - Logging functionality
- `get_current_time` - Timezone-aware timestamps

#### Line 17-18: Router Setup
```python
router = APIRouter(prefix="/auth/google", tags=["OAuth - Google"])
logger = setup_logger(__name__)
```

**Explanation:**
- Creates router with prefix `/auth/google`
- All routes will be: `/auth/google/login`, `/auth/google/callback`
- Tags group endpoints in Swagger documentation
- Logger for tracking OAuth events

#### Line 20-28: OAuth Client Configuration
```python
oauth = OAuth()
oauth.register(
    name='google',
    
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)
```

**Line by line:**
- **Line 20:** Create OAuth client instance
- **Line 21:** Register Google as OAuth provider
- **Line 22:** Name identifier for this provider
- **Line 23:** Your app's public ID from Google Cloud Console
- **Line 24:** Your app's secret key (like a password)
- **Line 25:** Google's configuration URL (auto-discovers OAuth endpoints)
- **Line 26:** Request access to: user ID, email, and profile name

**What `server_metadata_url` does:**
- Automatically fetches Google's OAuth endpoints
- Gets authorization URL, token URL, userinfo URL
- No need to hardcode these URLs

---

### Endpoint 1: `/auth/google/login` - Initiate Login

#### Line 31-35: Route Definition
```python
@router.get(
    "/login",
    summary="Login with Google",
    description="Redirect to Google OAuth login page"
)
```

**Explanation:**
- `@router.get` - HTTP GET endpoint
- URL: `/auth/google/login`
- `summary` - Short description for API docs
- `description` - Detailed description for API docs

#### Line 36-37: Function Signature
```python
async def google_login(request: Request):
    """
    Initiate Google OAuth login
    
    Redirects user to Google's OAuth consent screen
    """
```

**Explanation:**
- `async` - Asynchronous function (non-blocking)
- `request: Request` - Starlette request object (contains session)
- Docstring explains what function does

#### Line 43-45: Redirect Logic
```python
try:
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri)
```

**Line by line:**
- **Line 43:** Try block for error handling
- **Line 44:** Get callback URL from settings (`http://localhost:8000/auth/google/callback`)
- **Line 45:** 
  - Creates OAuth authorization URL
  - Generates random `state` parameter (security)
  - Stores state in session cookie
  - Redirects user to Google login page

**What happens behind the scenes:**
```
1. Generate random state: "abc123xyz"
2. Store in session cookie (encrypted)
3. Build URL: https://accounts.google.com/o/oauth2/auth?
   - client_id=YOUR_CLIENT_ID
   - redirect_uri=http://localhost:8000/auth/google/callback
   - state=abc123xyz
   - scope=openid email profile
4. Redirect user to this URL
```

#### Line 46-51: Error Handling
```python
except Exception as e:
    logger.error(f"Google OAuth login error: {str(e)}")
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to initiate Google login"
    )
```

**Explanation:**
- Catch any errors during redirect
- Log error for debugging
- Return 500 error to user with message

---

### Endpoint 2: `/auth/google/callback` - Handle Google Response

#### Line 54-58: Route Definition
```python
@router.get(
    "/callback",
    summary="Google OAuth Callback",
    description="Handle Google OAuth callback and create/login user"
)
```

**Explanation:**
- URL: `/auth/google/callback`
- Google redirects here after user authorizes
- This endpoint processes the OAuth response

#### Line 59-60: Function Signature
```python
async def google_callback(request: Request, db: Session = Depends(get_db)):
    """
    Handle Google OAuth callback
    
    - Creates new user if doesn't exist
    - Logs in existing user
    - Returns JWT token
    """
```

**Parameters:**
- `request` - Contains OAuth code and state from Google
- `db` - Database session (injected by FastAPI)

#### Line 68-69: Start Processing
```python
try:
    current_time = get_current_time()
```

**Explanation:**
- Try block for error handling
- Get current timestamp for logging

#### Line 71-72: Exchange Code for Token
```python
# Get token from Google
token = await oauth.google.authorize_access_token(request)
```

**What this does:**
1. Extracts `code` parameter from URL (sent by Google)
2. Verifies `state` matches session (security check)
3. Makes HTTP POST to Google's token endpoint:
   ```
   POST https://oauth2.googleapis.com/token
   {
     "code": "4/0AY0e-g7...",
     "client_id": "YOUR_CLIENT_ID",
     "client_secret": "YOUR_SECRET",
     "redirect_uri": "http://localhost:8000/auth/google/callback",
     "grant_type": "authorization_code"
   }
   ```
4. Google responds with access token and user info
5. Returns token object containing user data

#### Line 74-80: Extract User Info
```python
# Get user info from Google
user_info = token.get('userinfo')
if not user_info:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Failed to get user info from Google"
    )
```

**Explanation:**
- Extract user information from token
- If missing, return error (shouldn't happen normally)

#### Line 82-84: Parse User Data
```python
google_id = user_info.get('sub')
email = user_info.get('email')
full_name = user_info.get('name')
```

**What we get:**
- `sub` - Google's unique user ID (e.g., "1234567890")
- `email` - User's email (e.g., "john@gmail.com")
- `name` - Full name (e.g., "John Doe")

#### Line 86-91: Validate Data
```python
if not email or not google_id:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Email or Google ID not provided by Google"
    )
```

**Explanation:**
- Ensure we have required data
- Both email and google_id are mandatory

#### Line 93: Log Event
```python
logger.info(f"[{current_time}] Google OAuth: User {email} attempting login")
```

**Explanation:**
- Log OAuth attempt for auditing
- Includes timestamp and email

#### Line 95-96: Check by Google ID
```python
# Check if user exists by google_id
user = db.query(User).filter(User.google_id == google_id).first()
```

**SQL equivalent:**
```sql
SELECT * FROM users WHERE google_id = '1234567890' LIMIT 1;
```

**Why check google_id first:**
- User might have already linked Google account
- google_id is unique and never changes
- Faster lookup with index

#### Line 98-100: Check by Email
```python
# If not found by google_id, check by email
if not user:
    user = db.query(User).filter(User.email == email).first()
```

**SQL equivalent:**
```sql
SELECT * FROM users WHERE email = 'john@gmail.com' LIMIT 1;
```

**Why check email:**
- User might be registered but not linked to Google yet
- First time using Google login

#### Line 102-108: Link Existing Account
```python
# If user exists with email but no google_id, link the account
if user:
    user.google_id = google_id
    user.oauth_provider = 'google'
    db.commit()
    db.refresh(user)
    logger.info(f"[{current_time}] Linked existing user {email} with Google account")
```

**What happens:**
1. User registered with email/password before
2. Now using Google login for first time
3. Update user record:
   - Set `google_id` = "1234567890"
   - Set `oauth_provider` = "google"
4. Save to database
5. Refresh user object with updated data
6. Log the linking event

**SQL equivalent:**
```sql
UPDATE users 
SET google_id = '1234567890', oauth_provider = 'google' 
WHERE email = 'john@gmail.com';
```

#### Line 110-120: Reject New Users
```python
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
```

**Why reject:**
- No default role assignment
- User must register via `/auth/register` first
- Ensures explicit role selection
- Returns detailed error message

**Response example:**
```json
{
  "detail": {
    "error": "USER_NOT_REGISTERED",
    "message": "Please register first...",
    "email": "john@gmail.com",
    "google_id": "1234567890"
  }
}
```

#### Line 122-127: Check Active Status
```python
# Check if user is active
if not user.is_active:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User account is inactive"
    )
```

**Explanation:**
- Verify user account is not disabled
- Admin might have deactivated account
- Prevents inactive users from logging in

#### Line 129-133: Create JWT Token
```python
# Create access token
access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
access_token = create_access_token(
    data={"sub": user.email, "role": user.role.value, "user_id": str(user.id)},
    expires_delta=access_token_expires
)
```

**Line by line:**
- **Line 130:** Set expiration time (30 minutes from settings)
- **Line 131-133:** Create JWT token with:
  - `sub` - User's email (standard JWT claim)
  - `role` - User's role for RBAC
  - `user_id` - Database ID
  - `exp` - Expiration timestamp (added automatically)

**JWT token structure:**
```json
{
  "sub": "john@gmail.com",
  "role": "purchase_manager",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "exp": 1713456789
}
```

#### Line 135: Log Success
```python
logger.info(f"[{current_time}] User logged in via Google: {email}")
```

**Explanation:**
- Log successful login for auditing
- Includes timestamp and email

#### Line 137-150: Return Response
```python
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
```

**Response structure:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "john_doe",
    "email": "john@gmail.com",
    "full_name": "John Doe",
    "role": "purchase_manager",
    "oauth_provider": "google"
  }
}
```

**What user does with this:**
1. Store `access_token` in localStorage/cookies
2. Display user info in UI
3. Use token in API requests: `Authorization: Bearer TOKEN`

#### Line 152-158: Error Handling
```python
except HTTPException:
    raise
except Exception as e:
    logger.error(f"Google OAuth callback error: {str(e)}")
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"OAuth callback failed: {str(e)}"
    )
```

**Explanation:**
- Re-raise HTTPException (already formatted)
- Catch any other errors
- Log error details
- Return 500 error to user

---

### 2. `app/core/config.py` - Configuration

#### Added Lines
```python
# Google OAuth

GOOGLE_REDIRECT_URI: str = "http://localhost:8000/auth/google/callback"
```

**Explanation:**
- `GOOGLE_REDIRECT_URI` - Where Google sends user after login
- Values loaded from `.env` file

---

### 3. `.env` - Environment Variables

```

GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
```

**Explanation:**
- Never commit this file to Git (contains secrets)
- `CLIENT_ID` - From Google Cloud Console > Credentials
- `CLIENT_SECRET` - From Google Cloud Console > Credentials
- `REDIRECT_URI` - Must match exactly in Google Console

---

### 4. `app/main.py` - Session Middleware

#### Added Import
```python
from starlette.middleware.sessions import SessionMiddleware
from app.core.config import settings
```

**Explanation:**
- Import SessionMiddleware for OAuth state management
- Import settings to access SECRET_KEY

#### Added Middleware
```python
# Session middleware for OAuth
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY
)
```

**What it does:**
1. Creates encrypted session cookies
2. Stores OAuth state parameter
3. Verifies state on callback (prevents CSRF)
4. Uses `itsdangerous` library for encryption

**How it works:**
```
User visits /auth/google/login
  ↓
Middleware creates session cookie:
  session_id = encrypt({state: "abc123"})
  ↓
User goes to Google
  ↓
Google redirects back with state=abc123
  ↓
Middleware decrypts session cookie
  ↓
Verifies state matches
  ↓
If match → Continue
If no match → Reject (CSRF attack)
```

---

### 5. `app/models/user.py` - Database Schema

#### Added Fields
```python
google_id = Column(String, unique=True, nullable=True, index=True)
oauth_provider = Column(String, nullable=True)
hashed_password = Column(String, nullable=True)  # Changed from nullable=False
```

**Field explanations:**

**google_id:**
- Stores Google's unique user ID (e.g., "1234567890")
- `unique=True` - No duplicate Google accounts
- `nullable=True` - Not all users use Google
- `index=True` - Fast lookups

**oauth_provider:**
- Stores provider name: "google", "github", "facebook"
- `nullable=True` - Email/password users don't have this
- Future-proof for multiple OAuth providers

**hashed_password:**
- Changed to `nullable=True`
- OAuth users don't need passwords
- Email/password users still have passwords

---

### 6. `requirements.txt` - Dependencies

#### Added Lines
```
httpx==0.27.0
authlib==1.3.0
itsdangerous==2.1.2
```

**Dependency explanations:**

**httpx:**
- Modern HTTP client for Python
- Used by authlib to make OAuth requests
- Async support (faster than requests library)

**authlib:**
- OAuth 2.0 and OpenID Connect library
- Handles OAuth protocol complexity
- Supports multiple providers (Google, GitHub, etc.)

**itsdangerous:**
- Cryptographically signs data
- Used by SessionMiddleware
- Prevents session tampering

---

### 7. `migrate_oauth.py` - Database Migration

```python
import os
os.environ['DATABASE_URL'] = 'postgresql://postgres:2003@host.docker.internal:5432/procurementdb'

from sqlalchemy import text
from app.database.db import engine

def migrate():
    with engine.connect() as conn:
        try:
            # Add google_id column
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS google_id VARCHAR UNIQUE;
            """))
            
            # Add oauth_provider column
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS oauth_provider VARCHAR;
            """))
            
            # Make hashed_password nullable
            conn.execute(text("""
                ALTER TABLE users 
                ALTER COLUMN hashed_password DROP NOT NULL;
            """))
            
            # Create index on google_id
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_users_google_id 
                ON users(google_id);
            """))
            
            conn.commit()
            print("✅ Migration completed successfully!")
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Migration failed: {str(e)}")
            raise

if __name__ == "__main__":
    migrate()
```

**What it does:**
1. Connects to database
2. Adds `google_id` column
3. Adds `oauth_provider` column
4. Makes `hashed_password` optional
5. Creates index for fast lookups
6. Commits changes or rolls back on error

**Run once:**
```bash
docker exec procurement_app_oauth python migrate_oauth.py
```

---

## Flow Diagram

### Complete OAuth Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. User clicks "Login with Google" button                  │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Browser: GET /auth/google/login                         │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. Server:                                                  │
│    - Generate random state: "abc123"                        │
│    - Store in session cookie (encrypted)                    │
│    - Build Google OAuth URL                                 │
│    - Redirect to Google                                     │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. Google:                                                  │
│    - Show login page                                        │
│    - User enters email/password                             │
│    - Show consent screen                                    │
│    - User clicks "Allow"                                    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. Google redirects back:                                   │
│    GET /auth/google/callback?code=xyz&state=abc123          │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. Server:                                                  │
│    - Verify state matches session (security)                │
│    - Exchange code for access token                         │
│    - POST to Google's token endpoint                        │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 7. Google responds with:                                    │
│    {                                                        │
│      "access_token": "ya29.a0...",                          │
│      "userinfo": {                                          │
│        "sub": "1234567890",                                 │
│        "email": "john@gmail.com",                           │
│        "name": "John Doe"                                   │
│      }                                                      │
│    }                                                        │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 8. Server checks database:                                  │
│    - Query by google_id                                     │
│    - If not found, query by email                           │
└─────────────────────────────────────────────────────────────┘
                          ↓
         ┌────────────────┴────────────────┐
         ↓                                  ↓
┌──────────────────┐              ┌──────────────────┐
│ User exists      │              │ User not found   │
│ (registered)     │              │ (new user)       │
└──────────────────┘              └──────────────────┘
         ↓                                  ↓
┌──────────────────┐              ┌──────────────────┐
│ Link Google ID   │              │ Return error:    │
│ to account       │              │ "Please register │
└──────────────────┘              │  first"          │
         ↓                        └──────────────────┘
┌──────────────────┐
│ Generate JWT     │
│ token            │
└──────────────────┘
         ↓
┌──────────────────┐
│ Return token     │
│ and user info    │
└──────────────────┘
         ↓
┌──────────────────┐
│ User logged in!  │
└──────────────────┘
```

---

## Security Features

### 1. State Parameter (CSRF Protection)
```python
# Login endpoint generates random state
state = "abc123xyz"  # Random string
session['oauth_state'] = state  # Store in session

# Callback endpoint verifies state
if request.args['state'] != session['oauth_state']:
    raise Exception("CSRF attack detected!")
```

**Why needed:**
- Prevents Cross-Site Request Forgery attacks
- Ensures callback came from legitimate OAuth flow
- Attacker can't forge OAuth responses

### 2. Session Encryption
```python
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY  # Used to encrypt cookies
)
```

**What it does:**
- Encrypts session cookies with SECRET_KEY
- Uses `itsdangerous` library (HMAC signatures)
- Prevents cookie tampering

### 3. HTTPS (Production)
```python
# Production redirect URI
GOOGLE_REDIRECT_URI=https://yourdomain.com/auth/google/callback
```

**Why needed:**
- Encrypts data in transit
- Prevents man-in-the-middle attacks
- Required by Google for production apps

### 4. Token Expiration
```python
access_token_expires = timedelta(minutes=30)
```

**Why needed:**
- Limits damage if token is stolen
- Forces re-authentication after 30 minutes
- Industry standard practice

### 5. Unique google_id
```python
google_id = Column(String, unique=True, nullable=True, index=True)
```

**Why needed:**
- Prevents duplicate Google accounts
- Database enforces uniqueness
- Can't create multiple accounts with same Google ID

---

## Testing Guide

### Test 1: New User (Not Registered)
```bash
# Step 1: Try Google login
GET http://localhost:8000/auth/google/login

# Expected: Redirects to Google
# After Google login: Error message
{
  "detail": {
    "error": "USER_NOT_REGISTERED",
    "message": "Please register first..."
  }
}
```

### Test 2: Register Then Link Google
```bash
# Step 1: Register with email/password
POST http://localhost:8000/auth/register
{
  "username": "john_doe",
  "email": "john@gmail.com",
  "password": "password123",
  "role": "purchase_manager",
  "full_name": "John Doe"
}

# Step 2: Login with Google (same email)
GET http://localhost:8000/auth/google/login

# Expected: Success! Account linked
{
  "access_token": "eyJhbGci...",
  "user": {
    "email": "john@gmail.com",
    "role": "purchase_manager",
    "oauth_provider": "google"
  }
}
```

### Test 3: Use Token
```bash
# Use token in API requests
GET http://localhost:8000/auth/me
Authorization: Bearer eyJhbGci...

# Expected: User info
{
  "id": "123e4567...",
  "username": "john_doe",
  "email": "john@gmail.com",
  "role": "purchase_manager"
}
```

---

## Common Issues & Solutions

### Issue 1: "Error 400: invalid_request"
**Cause:** Redirect URI not configured in Google Console  
**Solution:** Add `http://localhost:8000/auth/google/callback` to authorized redirect URIs

### Issue 2: "SessionMiddleware must be installed"
**Cause:** Missing SessionMiddleware in main.py  
**Solution:** Add SessionMiddleware before routes

### Issue 3: "No module named 'itsdangerous'"
**Cause:** Missing dependency  
**Solution:** `pip install itsdangerous`

### Issue 4: "State mismatch"
**Cause:** Session cookie not working  
**Solution:** Check SECRET_KEY is set in .env

---

## Production Checklist

- [ ] Change SECRET_KEY to strong random value
- [ ] Use HTTPS (not HTTP)
- [ ] Update GOOGLE_REDIRECT_URI to production domain
- [ ] Add production redirect URI to Google Console
- [ ] Set CORS allow_origins to specific domains
- [ ] Enable rate limiting
- [ ] Set up monitoring and logging
- [ ] Use secrets manager (not .env file)
- [ ] Enable database SSL
- [ ] Add health checks

---

## Summary

This OAuth implementation provides:
- ✅ Secure Google login
- ✅ No default role assignment (explicit registration required)
- ✅ Account linking for existing users
- ✅ CSRF protection with state parameter
- ✅ Session encryption
- ✅ JWT token generation
- ✅ Production-ready architecture

Users must register first to choose their role, then can link Google for convenient login.
