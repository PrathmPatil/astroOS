from fastapi import APIRouter

from app.schemas import GunMilanRequest, GunMilanResponse, MatchmakingResponse
from app.services.matchmaking_service import (
    compute_gun_milan_enriched,
    kundali_matching,
)

router = APIRouter()


@router.post("/gun-milan", response_model=GunMilanResponse)
def gun_milan_route(payload: GunMilanRequest) -> GunMilanResponse:
    return GunMilanResponse(**compute_gun_milan_enriched(payload))


@router.post("/matchmaking", response_model=MatchmakingResponse)
def matchmaking(payload: GunMilanRequest) -> MatchmakingResponse:
    """Traditional + modern + AI-combined kundali matching."""
    return MatchmakingResponse(**kundali_matching(payload))


@router.post("/compatibility", response_model=MatchmakingResponse)
def compatibility(payload: GunMilanRequest) -> MatchmakingResponse:
    """Alias focused on advanced compatibility aggregate."""
    return MatchmakingResponse(**kundali_matching(payload))
