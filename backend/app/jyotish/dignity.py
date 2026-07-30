"""Planetary dignity: exaltation, own sign, friend/enemy, combust."""

from __future__ import annotations

from dataclasses import dataclass

from app.core.constants import (
    COMBUSTION_ORB,
    DEBILITATION,
    EXALTATION,
    OWN_SIGNS,
    SIGN_LORDS,
)
from app.jyotish.utils import sign_from_longitude

# Natural friendship (simplified classical table)
NATURAL_FRIENDS: dict[str, set[str]] = {
    "Sun": {"Moon", "Mars", "Jupiter"},
    "Moon": {"Sun", "Mercury"},
    "Mars": {"Sun", "Moon", "Jupiter"},
    "Mercury": {"Sun", "Venus"},
    "Jupiter": {"Sun", "Moon", "Mars"},
    "Venus": {"Mercury", "Saturn"},
    "Saturn": {"Mercury", "Venus"},
}

NATURAL_ENEMIES: dict[str, set[str]] = {
    "Sun": {"Venus", "Saturn"},
    "Moon": {},
    "Mars": {"Mercury"},
    "Mercury": {"Moon"},
    "Jupiter": {"Mercury", "Venus"},
    "Venus": {"Sun", "Moon"},
    "Saturn": {"Sun", "Moon", "Mars"},
}


@dataclass(slots=True)
class Dignity:
    exalted: bool
    debilitated: bool
    own_sign: bool
    dig_bala_hint: str
    relationship_to_sign_lord: str  # friend | enemy | neutral | own
    combust: bool
    combustion_orb_used: float | None


def is_combust(
    planet: str,
    planet_lon: float,
    sun_lon: float,
    retrograde: bool = False,
) -> tuple[bool, float | None]:
    if planet in {"Sun", "Rahu", "Ketu", "Uranus", "Neptune", "Pluto"}:
        return False, None
    orb = COMBUSTION_ORB.get(planet)
    if orb is None:
        return False, None
    if planet == "Mercury" and retrograde:
        orb = 12.0
    if planet == "Venus" and retrograde:
        orb = 8.0
    diff = abs((planet_lon - sun_lon + 180) % 360 - 180)
    return diff <= orb, orb


def evaluate_dignity(
    planet: str,
    longitude: float,
    sun_longitude: float | None = None,
    retrograde: bool = False,
) -> Dignity:
    sign = sign_from_longitude(longitude).sign_index
    exalted = EXALTATION.get(planet) == sign
    debilitated = DEBILITATION.get(planet) == sign
    own = sign in OWN_SIGNS.get(planet, [])

    sign_lord = SIGN_LORDS[sign]
    if own or planet == sign_lord:
        rel = "own"
    elif planet in NATURAL_FRIENDS and sign_lord in NATURAL_FRIENDS.get(planet, set()):
        rel = "friend"
    elif planet in NATURAL_ENEMIES and sign_lord in NATURAL_ENEMIES.get(planet, set()):
        rel = "enemy"
    else:
        rel = "neutral"

    combust = False
    orb_used = None
    if sun_longitude is not None:
        combust, orb_used = is_combust(planet, longitude, sun_longitude, retrograde)

    return Dignity(
        exalted=exalted,
        debilitated=debilitated,
        own_sign=own,
        dig_bala_hint="pending_full_shadbala",
        relationship_to_sign_lord=rel,
        combust=combust,
        combustion_orb_used=orb_used,
    )
