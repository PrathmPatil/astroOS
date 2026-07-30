from datetime import datetime

from fastapi import APIRouter

from app.schemas import BirthDetails, TransitRequest
from app.services.analysis_service import compute_transit

router = APIRouter()


@router.post("/transit")
def transit(payload: TransitRequest) -> dict:
    return compute_transit(payload.birth, payload.at)


@router.post("/transit/now")
def transit_now(payload: BirthDetails, at: datetime | None = None) -> dict:
    return compute_transit(payload, at)
