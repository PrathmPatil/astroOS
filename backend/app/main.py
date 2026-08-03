"""AstroSutra AI — FastAPI entrypoint."""

from __future__ import annotations

import re
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        origin = request.headers.get("origin", "")
        headers: dict[str, str] = {}
        allowed = False
        if origin in settings.cors_origin_list:
            allowed = True
        elif settings.cors_origin_regex and re.fullmatch(
            settings.cors_origin_regex, origin or ""
        ):
            allowed = True
        if allowed and origin:
            headers["Access-Control-Allow-Origin"] = origin
            headers["Access-Control-Allow-Credentials"] = "true"
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "error": str(exc)[:500],
                "path": str(request.url.path),
            },
            headers=headers,
        )

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
