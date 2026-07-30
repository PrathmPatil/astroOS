"""Pydantic request/response schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class BirthDetails(BaseModel):
    name: str | None = None
    year: int = Field(..., ge=1800, le=2200)
    month: int = Field(..., ge=1, le=12)
    day: int = Field(..., ge=1, le=31)
    hour: int = Field(..., ge=0, le=23)
    minute: int = Field(..., ge=0, le=59)
    second: float = Field(0, ge=0, lt=60)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    timezone: str = Field(..., description="IANA timezone, e.g. Asia/Kolkata")
    place: str | None = None
    ayanamsha: Literal["lahiri", "raman", "krishnamurti"] = "lahiri"
    house_system: str = "W"


class PlanetOut(BaseModel):
    name: str
    longitude: float
    sign: str
    sign_mr: str
    degree_in_sign: float
    dms: str
    nakshatra: str
    pada: int
    nakshatra_lord: str
    house: int
    retrograde: bool
    exalted: bool
    debilitated: bool
    own_sign: bool
    combust: bool
    relationship_to_sign_lord: str


class HouseOut(BaseModel):
    number: int
    cusp_longitude: float
    sign: str
    sign_lord: str


class LagnaOut(BaseModel):
    longitude: float
    sign: str
    sign_mr: str
    dms: str
    lord: str
    nakshatra: str
    pada: int


class BirthChartResponse(BaseModel):
    meta: dict[str, Any]
    lagna: LagnaOut
    planets: list[PlanetOut]
    houses: list[HouseOut]
    moon: dict[str, Any]
    ayanamsha_value: float
    disclaimer: str


class VargasResponse(BaseModel):
    meta: dict[str, Any]
    vargas: dict[str, list[dict[str, Any]]]
    disclaimer: str


class DashaPeriodOut(BaseModel):
    lord: str
    start: datetime
    end: datetime
    level: str
    parent: str | None = None


class DashaResponse(BaseModel):
    current_mahadasha: DashaPeriodOut
    current_antardasha: DashaPeriodOut
    mahadashas: list[DashaPeriodOut]
    antardashas: list[DashaPeriodOut]
    disclaimer: str


class YogaOut(BaseModel):
    key: str
    name: str
    present: bool
    strength: str
    planets_involved: list[str]
    notes: str


class YogasResponse(BaseModel):
    yogas: list[YogaOut]
    present_count: int
    disclaimer: str


class DoshaOut(BaseModel):
    key: str
    name: str
    present: bool
    severity: str
    details: str
    houses_or_planets: list[str]


class DoshaResponse(BaseModel):
    doshas: list[DoshaOut]
    present_count: int
    disclaimer: str


class GunMilanRequest(BaseModel):
    boy: BirthDetails
    girl: BirthDetails


class KootaOut(BaseModel):
    name: str
    obtained: float
    maximum: float
    notes: str


class GunMilanResponse(BaseModel):
    total: float
    maximum: float
    percentage: float
    verdict: str
    kootas: list[KootaOut]
    boy_nakshatra: str
    girl_nakshatra: str
    boy_rasi: str
    girl_rasi: str
    strengths: list[str] = []
    weaknesses: list[str] = []
    dosha_checks: dict[str, bool] | None = None
    disclaimer: str


class CompatibilityDimensionOut(BaseModel):
    key: str
    label: str
    score: float
    band: str
    detail: str
    factors: list[str]


class MatchmakingResponse(BaseModel):
    profiles: dict
    traditional: dict
    modern: dict
    ai_combined: dict
    modes: dict[str, float]
    disclaimer: str


class AIAnalysisRequest(BaseModel):
    birth: BirthDetails
    language: Literal["en", "mr", "hi"] = "mr"
    focus: Literal[
        "overview",
        "career",
        "marriage",
        "health",
        "wealth",
        "dasha",
    ] = "overview"


class AIAnalysisResponse(BaseModel):
    language: str
    focus: str
    analysis: str
    provider: str
    chart_summary: dict[str, Any]
    disclaimer: str


class TransitRequest(BaseModel):
    birth: BirthDetails
    at: datetime | None = None


class HealthResponse(BaseModel):
    status: str
    version: str
    ephemeris_path: str
