"""Main FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import sys

from app.config import settings
from app.routers import health, users, items, uc_calculator
from app.middleware.cors import get_cors_middleware


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION,
    )

    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(health.router, tags=["health"])
    app.include_router(users.router, prefix="/api/users", tags=["users"])
    app.include_router(items.router, prefix="/api/items", tags=["items"])
    app.include_router(uc_calculator.router, prefix="/api/uc", tags=["universal-credit"])

    @app.on_event("startup")
    def run_migrations():
        """Run Alembic migrations on startup."""
        try:
            subprocess.run(
                [sys.executable, "-m", "alembic", "upgrade", "head"],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to run migrations: {e}")

    return app


app = create_app()
