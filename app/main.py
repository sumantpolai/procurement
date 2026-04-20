from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database.db import engine, Base
from app.database.db import check_db_connection
import logging


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
    
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(lifespan=lifespan)

# Add CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(
    tags=["Items"],
    router=__import__("app.routes.item_routes", fromlist=["router"]).router
)




