"""Vercel FastAPI entrypoint — re-exports the AstroOS ASGI app."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"

if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

os.environ.setdefault("ASTROOS_ROOT", str(ROOT))
os.environ.setdefault("SE_EPHE_PATH", str(BACKEND / "ephe"))
os.environ.setdefault("APP_ENV", "production")
os.environ.setdefault("DEBUG", "false")
os.environ.setdefault("AI_PROVIDER", "none")
os.environ.setdefault(
    "CORS_ORIGINS",
    "https://astroos-one.vercel.app,"
    "https://astroos.vercel.app,"
    "http://localhost:3000,"
    "http://localhost:3001,"
    "http://127.0.0.1:3000,"
    "http://127.0.0.1:3001",
)
os.environ.setdefault(
    "CORS_ORIGIN_REGEX",
    r"https://.*\.vercel\.app",
)

from app.main import app  # noqa: E402

__all__ = ["app"]
