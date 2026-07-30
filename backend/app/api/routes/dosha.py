from fastapi import APIRouter

from app.schemas import BirthDetails, DoshaResponse
from app.services.analysis_service import compute_doshas

router = APIRouter()


@router.post("/dosha", response_model=DoshaResponse)
def dosha(payload: BirthDetails) -> DoshaResponse:
    return DoshaResponse(**compute_doshas(payload))
