from fastapi import APIRouter

from app.astronomy.ephemeris import ephemeris_engine, init_ephemeris
from app.core.config import get_settings
from app.schemas import HealthResponse
from app import __version__

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    settings = get_settings()
    path = init_ephemeris()
    return HealthResponse(
        status="ok",
        version=__version__,
        ephemeris_path=f"{path} [{ephemeris_engine()}]",
    )
