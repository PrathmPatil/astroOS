"""Longitude helpers: signs, DMS, nakshatra, pada."""

from __future__ import annotations

from dataclasses import dataclass

from app.core.constants import (
    NAKSHATRA_LORDS,
    NAKSHATRAS,
    SIGNS,
    SIGNS_HI,
    SIGNS_MR,
)

NAKSHATRA_SPAN = 360.0 / 27.0  # 13°20'
PADA_SPAN = NAKSHATRA_SPAN / 4.0  # 3°20'


@dataclass(slots=True)
class SignPlacement:
    sign_index: int
    sign: str
    sign_mr: str
    sign_hi: str
    degree_in_sign: float
    degrees: int
    minutes: int
    seconds: int


@dataclass(slots=True)
class NakshatraPlacement:
    index: int
    name: str
    lord: str
    pada: int
    degree_in_nakshatra: float


def split_dms(longitude: float) -> tuple[int, int, int, float]:
    """Return (deg_in_sign, minutes, seconds, sign_index_float_part unused)."""
    lon = longitude % 360.0
    sign_index = int(lon // 30)
    deg_in_sign = lon % 30.0
    degrees = int(deg_in_sign)
    minutes_full = (deg_in_sign - degrees) * 60.0
    minutes = int(minutes_full)
    seconds = int(round((minutes_full - minutes) * 60.0))
    if seconds == 60:
        seconds = 0
        minutes += 1
    if minutes == 60:
        minutes = 0
        degrees += 1
    return degrees, minutes, seconds, sign_index


def sign_from_longitude(longitude: float) -> SignPlacement:
    lon = longitude % 360.0
    degrees, minutes, seconds, sign_index = split_dms(lon)
    return SignPlacement(
        sign_index=int(sign_index),
        sign=SIGNS[int(sign_index)],
        sign_mr=SIGNS_MR[int(sign_index)],
        sign_hi=SIGNS_HI[int(sign_index)],
        degree_in_sign=lon % 30.0,
        degrees=degrees,
        minutes=minutes,
        seconds=seconds,
    )


def nakshatra_from_longitude(longitude: float) -> NakshatraPlacement:
    lon = longitude % 360.0
    idx = int(lon // NAKSHATRA_SPAN) % 27
    within = lon % NAKSHATRA_SPAN
    pada = int(within // PADA_SPAN) + 1
    return NakshatraPlacement(
        index=idx,
        name=NAKSHATRAS[idx],
        lord=NAKSHATRA_LORDS[idx],
        pada=min(max(pada, 1), 4),
        degree_in_nakshatra=within,
    )


def absolute_degree_string(longitude: float) -> str:
    sp = sign_from_longitude(longitude)
    return f"{sp.degrees}° {sp.sign} {sp.minutes:02d}' {sp.seconds:02d}\""
