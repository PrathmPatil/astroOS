from datetime import datetime

from fastapi import APIRouter

from app.schemas import BirthDetails, DashaResponse
from app.services.analysis_service import compute_dasha

router = APIRouter()


@router.post("/dasha", response_model=DashaResponse)
def dasha(payload: BirthDetails, at: datetime | None = None) -> DashaResponse:
    return DashaResponse(**compute_dasha(payload, at))
