import json
from datetime import timedelta
from typing import Any, Dict
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from jose import JWTError, jwt
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token

from app.core.config import settings
from app.core.timezone import get_current_time


GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_SCOPES = ["openid", "email", "profile"]


def create_google_oauth_state() -> str:
    """Create a short-lived state token to protect the OAuth callback."""
    now = get_current_time()
    expire = now + timedelta(minutes=settings.GOOGLE_OAUTH_STATE_EXPIRE_MINUTES)
    payload = {
        "type": "google_oauth_state",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_google_oauth_state(state: str) -> Dict[str, Any]:
    """Verify the Google OAuth state token."""
    try:
        payload = jwt.decode(state, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError as exc:
        raise ValueError("Invalid OAuth state") from exc

    if payload.get("type") != "google_oauth_state":
        raise ValueError("Invalid OAuth state")

    return payload


def build_google_authorization_url(state: str) -> str:
    """Build the authorization URL used to start the Google login flow."""
    query = urlencode(
        {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": " ".join(GOOGLE_SCOPES),
            "access_type": "offline",
            "prompt": "consent",
            "include_granted_scopes": "true",
            "state": state,
        }
    )
    return f"{GOOGLE_AUTH_URL}?{query}"


def exchange_code_for_tokens(code: str) -> Dict[str, Any]:
    """Exchange an authorization code for Google tokens."""
    payload = urlencode(
        {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }
    ).encode("utf-8")
    request = Request(
        GOOGLE_TOKEN_URL,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )

    with urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def verify_google_identity_token(token: str) -> Dict[str, Any]:
    """Verify the Google ID token and return user claims."""
    request = google_requests.Request()
    payload = google_id_token.verify_oauth2_token(token, request, settings.GOOGLE_CLIENT_ID)

    if payload.get("iss") not in {"accounts.google.com", "https://accounts.google.com"}:
        raise ValueError("Invalid Google token issuer")

    if not payload.get("email_verified"):
        raise ValueError("Google account email is not verified")

    return payload
