"""Approximate sidereal positions for local Windows/dev when pyswisseph is unavailable.

NOT for production accuracy — Swiss Ephemeris is required for SaaS / published charts.
Uses low-precision mean elements suitable for wiring the rule engine & APIs.
"""

from __future__ import annotations

import math
from functools import lru_cache

from app.astronomy.backend import HouseBundle
from app.astronomy.planets import PlanetPosition

# Rough mean longitudes / daily motions at J2000 (tropical), degrees
# Enough to exercise dasha/yoga/gun-milan pipelines during development.
_MEAN = {
    "Sun": (280.460, 0.9856474),
    "Moon": (218.316, 13.176396),
    "Mercury": (252.251, 4.092317),
    "Venus": (181.980, 1.602130),
    "Mars": (355.453, 0.524033),
    "Jupiter": (34.351, 0.083091),
    "Saturn": (50.077, 0.033460),
    "Uranus": (314.055, 0.011748),
    "Neptune": (304.349, 0.005981),
    "Pluto": (238.929, 0.003968),
    "Rahu": (125.045, -0.052954),  # mean node regresses
}

LAHIRI_AYANAMSHA_J2000 = 23.85  # approx
AYAN_RATE = 0.013972  # deg/year rough


def _norm(x: float) -> float:
    return x % 360.0


def _jd_to_years_from_j2000(jd_ut: float) -> float:
    return (jd_ut - 2451545.0) / 365.25


def approx_ayanamsha(jd_ut: float, name: str = "lahiri") -> float:
    years = _jd_to_years_from_j2000(jd_ut)
    base = LAHIRI_AYANAMSHA_J2000 + years * AYAN_RATE
    if name == "raman":
        return base - 1.4
    if name == "krishnamurti":
        return base - 0.1
    return base


def _tropical(jd_ut: float, body: str) -> tuple[float, float]:
    if body == "Ketu":
        lon, speed = _tropical(jd_ut, "Rahu")
        return _norm(lon + 180.0), -speed
    lon0, daily = _MEAN[body]
    days = jd_ut - 2451545.0
    lon = _norm(lon0 + daily * days)
    return lon, daily


def approx_planet(jd_ut: float, name: str, ayanamsha: str = "lahiri") -> PlanetPosition:
    trop, speed = _tropical(jd_ut, name)
    ayan = approx_ayanamsha(jd_ut, ayanamsha)
    sid = _norm(trop - ayan)
    return PlanetPosition(
        name=name,
        longitude=sid,
        latitude=0.0,
        distance=1.0,
        speed_longitude=speed,
        retrograde=speed < 0,
        tropical_longitude=trop,
    )


def approx_houses(
    jd_ut: float,
    latitude: float,
    longitude: float,
    house_system: str = "W",
    ayanamsha: str = "lahiri",
) -> HouseBundle:
    """Rough RAMC / Ascendant using sidereal local sidereal time approximation."""
    # Local sidereal time approx
    days = jd_ut - 2451545.0
    gmst = _norm(280.46061837 + 360.98564736629 * days)
    lst = _norm(gmst + longitude)
    ayan = approx_ayanamsha(jd_ut, ayanamsha)
    # Obliquity
    eps = math.radians(23.4393)
    lat = math.radians(latitude)
    ramc = math.radians(lst)
    # Ascendant formula
    asc_trop = math.degrees(
        math.atan2(
            math.cos(ramc),
            -(math.sin(ramc) * math.cos(eps) + math.tan(lat) * math.sin(eps)),
        )
    )
    asc_trop = _norm(asc_trop)
    mc_trop = _norm(lst)
    asc = _norm(asc_trop - ayan)
    mc = _norm(mc_trop - ayan)

    if house_system.upper() == "W":
        lagna_sign = int(asc // 30)
        cusps = [((lagna_sign + i) % 12) * 30.0 for i in range(12)]
    else:
        cusps = [_norm(asc + i * 30.0) for i in range(12)]

    return HouseBundle(
        system=house_system.upper(),
        cusps=cusps,
        ascendant=asc,
        mc=mc,
        armc=lst,
        vertex=_norm(asc + 180),
    )


@lru_cache
def swe_available() -> bool:
    try:
        import swisseph  # noqa: F401

        return True
    except Exception:
        return False
