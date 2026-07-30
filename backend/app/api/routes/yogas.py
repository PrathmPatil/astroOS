from fastapi import APIRouter

from app.schemas import BirthDetails, YogasResponse
from app.services.analysis_service import compute_yogas

router = APIRouter()


@router.post("/yogas", response_model=YogasResponse)
def yogas(payload: BirthDetails) -> YogasResponse:
    return YogasResponse(**compute_yogas(payload))
