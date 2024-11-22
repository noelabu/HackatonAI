from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import Settings
from app.api.main import api_router

def create_app(
    settings: Settings | None = None,
) -> FastAPI:
    """Create a new app from application settings"""

    if settings is None:
        settings = Settings()

    app = FastAPI()

    if settings.CORS_ENABLED:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ALLOWED_ORIGINS,
            allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
            allow_methods=settings.CORS_ALLOWED_METHODS,
            allow_headers=settings.CORS_ALLOWED_HEADERS,
        )

    app.include_router(api_router)
    return app
