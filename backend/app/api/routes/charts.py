from fastapi import APIRouter

from app.schemas import BirthChartResponse, BirthDetails, PlanetOut, VargasResponse
from app.services.chart_service import compute_chart, compute_vargas

router = APIRouter()


@router.post("/birth-chart", response_model=BirthChartResponse)
def birth_chart(payload: BirthDetails) -> BirthChartResponse:
    data = compute_chart(payload)
    return BirthChartResponse(
        meta=data["meta"],
        lagna=data["lagna"],
        planets=data["planets"],
        houses=data["houses"],
        moon=data["moon"],
        ayanamsha_value=data["ayanamsha_value"],
        disclaimer=data["disclaimer"],
    )


@router.post("/planets", response_model=list[PlanetOut])
def planets(payload: BirthDetails) -> list[PlanetOut]:
    data = compute_chart(payload)
    return data["planets"]


@router.post("/navamsa")
def navamsa(payload: BirthDetails) -> dict:
    data = compute_vargas(payload)
    return {
        "meta": data["meta"],
        "d9": data["vargas"].get("D9", []),
        "disclaimer": data["disclaimer"],
    }


@router.post("/vargas", response_model=VargasResponse)
def vargas(payload: BirthDetails) -> VargasResponse:
    data = compute_vargas(payload)
    return VargasResponse(**data)
