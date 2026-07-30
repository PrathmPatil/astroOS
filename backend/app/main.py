"""AstroSutra AI — FastAPI entrypoint."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api import api_router
from app.astronomy.ephemeris import init_ephemeris
from app.core.config import get_settings
from app.core.constants import DISCLAIMER_EN


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_ephemeris()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        description=(
            "Professional Vedic Astrology Analysis Engine. "
            + DISCLAIMER_EN
        ),
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_origin_regex=settings.cors_origin_regex or None,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    @app.get("/")
    def root() -> dict:
        return {
            "name": settings.app_name,
            "version": __version__,
            "docs": "/docs",
            "health": f"{settings.api_v1_prefix}/health",
            "disclaimer": DISCLAIMER_EN,
        }

    return app


app = create_app()
