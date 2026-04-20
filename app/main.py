from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.db import engine, Base
from app.database.db import check_db_connection
from app.routes import pr, po
from app.core.logger import setup_logger
import logging
from app.api.api import api_router
from app.models import *


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    logger.info("🚀 Starting up the application...")
    
    check_db_connection()
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables created successfully")
    
    yield
    # Shutdown code
    logger.info("🛑 Shutting down the application...")
    
app = FastAPI(
    title="Procurement Management System",
    description="Production-level API for managing Purchase Requests, Purchase Orders, Items, and Vendors",
    version="1.0.0",
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

# Include routes
app.include_router(pr.router)
app.include_router(po.router)


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Procurement Management System API is running"
    }

app.include_router(
    tags=["Items"],
    router=__import__("app.routes.item_routes", fromlist=["router"]).router
)


app.include_router(api_router, prefix="/api")



