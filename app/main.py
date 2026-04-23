from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.database.db import engine, Base
from app.database.db import check_db_connection
from app.api.routes.pr import router as pr_router
from app.api.routes.po import router as po_router
from app.api.routes.item import router as item_router
from app.routes.auth import router as auth_router
from app.routes.oauth import router as oauth_router
from app.core.logger import setup_logger
from app.core.timezone import get_current_time
from app.core.config import settings
import logging
from app.api.api import api_router
from app.models import *


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    current_time = get_current_time()
    logger.info(f"[{current_time}] 🚀 Starting up the application...")
    
    check_db_connection()
    Base.metadata.create_all(bind=engine)
    logger.info(f"[{current_time}] ✅ Database tables created successfully")
    
    yield
    # Shutdown code
    current_time = get_current_time()
    logger.info(f"[{current_time}] 🛑 Shutting down the application...")
    
app = FastAPI(
    title="Procurement Management System",
    description="Production-level API for managing Purchase Requests, Purchase Orders, Items, and Vendors with Email/Password Authentication",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session middleware for OAuth
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY
)

# Include routes
app.include_router(auth_router)
app.include_router(oauth_router)
app.include_router(pr_router)
app.include_router(po_router)
app.include_router(item_router)
app.include_router(api_router)


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    current_time = get_current_time()
    return {
        "status": "healthy",
        "message": "Procurement Management System API is running",
        "timezone": str(current_time.tzinfo),
        "current_time": current_time.isoformat()
    }



