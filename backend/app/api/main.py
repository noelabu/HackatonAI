from fastapi import APIRouter
from app.api.routes import openai
from app.api.routes import listing

api_router = APIRouter()
api_router.include_router(openai.router, tags=["OpenAI"])
api_router.include_router(listing.router, tags=["Listing Property"])