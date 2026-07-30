"""Planetary position calculations (sidereal)."""

from __future__ import annotations

from dataclasses import dataclass

from app.astronomy.ephemeris import init_ephemeris, set_ayanamsha, _try_import_swe
from app.core.constants import PLANET_KEYS


@dataclass(slots=True)
class PlanetPosition:
    name: str
    longitude: float  # sidereal 0–360
    latitude: float
    distance: float
    speed_longitude: float
    retrograde: bool
    tropical_longitude: float


def _normalize(lon: float) -> float:
    return lon % 360.0


def calc_planet(
    jd_ut: float,
    name: str,
    ayanamsha: str = "lahiri",
) -> PlanetPosition:
    init_ephemeris()
    swe = _try_import_swe()
    if not swe:
        from app.astronomy.approx import approx_planet

        return approx_planet(jd_ut, name, ayanamsha)

    set_ayanamsha(ayanamsha)
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_SIDEREAL
    planet_ids = {
        "Sun": swe.SUN,
        "Moon": swe.MOON,
        "Mercury": swe.MERCURY,
        "Venus": swe.VENUS,
        "Mars": swe.MARS,
        "Jupiter": swe.JUPITER,
        "Saturn": swe.SATURN,
        "Uranus": swe.URANUS,
        "Neptune": swe.NEPTUNE,
        "Pluto": swe.PLUTO,
        "Rahu": swe.TRUE_NODE,
    }

    if name == "Ketu":
        xx, _ret = swe.calc_ut(jd_ut, planet_ids["Rahu"], flags)
        lon = _normalize(xx[0] + 180.0)
        return PlanetPosition(
            name="Ketu",
            longitude=lon,
            latitude=-xx[1],
            distance=xx[2],
            speed_longitude=-xx[3],
            retrograde=True,
            tropical_longitude=_normalize(lon + swe.get_ayanamsa_ut(jd_ut)),
        )

    body = planet_ids[name]
    xx, _ret = swe.calc_ut(jd_ut, body, flags)
    speed = float(xx[3])
    return PlanetPosition(
        name=name,
        longitude=_normalize(float(xx[0])),
        latitude=float(xx[1]),
        distance=float(xx[2]),
        speed_longitude=speed,
        retrograde=speed < 0,
        tropical_longitude=_normalize(float(xx[0]) + swe.get_ayanamsa_ut(jd_ut)),
    )


def calc_all_planets(
    jd_ut: float,
    ayanamsha: str = "lahiri",
    include_outer: bool = True,
) -> dict[str, PlanetPosition]:
    keys = PLANET_KEYS if include_outer else [
        p for p in PLANET_KEYS if p not in {"Uranus", "Neptune", "Pluto"}
    ]
    return {name: calc_planet(jd_ut, name, ayanamsha) for name in keys}


def get_ayanamsha_value(jd_ut: float, ayanamsha: str = "lahiri") -> float:
    init_ephemeris()
    swe = _try_import_swe()
    if not swe:
        from app.astronomy.approx import approx_ayanamsha

        return approx_ayanamsha(jd_ut, ayanamsha)
    set_ayanamsha(ayanamsha)
    return float(swe.get_ayanamsa_ut(jd_ut))
