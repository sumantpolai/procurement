from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database.db import engine, Base
from app.database.db import check_db_connection
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
    logger.info("🚀 Starting up the application...")
    
    check_db_connection()
    Base.metadata.create_all(bind=engine)
    
    yield
    # Shutdown code
    
app = FastAPI(lifespan=lifespan)

app.include_router(api_router, prefix="/api")



