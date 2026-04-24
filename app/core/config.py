from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    TIMEZONE: str = "Asia/Kolkata"  # Indian Standard Time
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str
    GOOGLE_OAUTH_DEFAULT_ROLE: str = "store_staff"
    GOOGLE_OAUTH_STATE_EXPIRE_MINUTES: int = 10
    
    class Config:
        env_file = ".env"
        

settings = Settings()
