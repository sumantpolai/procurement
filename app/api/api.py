from fastapi import APIRouter
from app.api.routes import vendor

api_router = APIRouter()

api_router.include_router(vendor.router, prefix="/vendors", tags=["Vendors"])