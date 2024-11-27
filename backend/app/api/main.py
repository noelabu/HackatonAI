from fastapi import APIRouter

from app.api.routes import listing
from app.api.routes import validation

api_router = APIRouter()
api_router.include_router(validation.router, tags=["Property Validation"])
api_router.include_router(listing.router, tags=["Listing Property"])