from fastapi import APIRouter

from app.schemas import BirthDetails
from app.services.marriage_service import (
    marriage_full_report,
    marriage_love_only,
    marriage_spouse_only,
    marriage_timing_only,
)

router = APIRouter(prefix="/marriage")


@router.post("/overview")
def marriage_overview(payload: BirthDetails) -> dict:
    """Full marriage microservice aggregate."""
    return marriage_full_report(payload)


@router.post("/timing")
def marriage_timing(payload: BirthDetails) -> dict:
    return marriage_timing_only(payload)


@router.post("/spouse")
def marriage_spouse(payload: BirthDetails) -> dict:
    return marriage_spouse_only(payload)


@router.post("/love-probability")
def marriage_love(payload: BirthDetails) -> dict:
    return marriage_love_only(payload)
