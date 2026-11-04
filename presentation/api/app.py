"""Factory for the local ZeroUI-AC HTTP API."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from presentation.api.routes import create_router


LOCAL_FRONTEND_ORIGINS = (
    "http://localhost:8100",
    "http://127.0.0.1:8100",
    "http://localhost:4200",
    "http://127.0.0.1:4200",
)


def create_app(facade):
    """Create an API instance backed by an already-constructed facade."""
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(LOCAL_FRONTEND_ORIGINS),
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )
    app.include_router(create_router(facade), prefix="/api")
    return app
