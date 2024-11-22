from fastapi import APIRouter
from app.api.routes import openai

api_router = APIRouter()
api_router.include_router(openai.router, tags=["OpenAI"])