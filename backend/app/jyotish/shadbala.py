"""Classical Shadbala (six-fold strength) — virupa-based implementation.

Full Parashari tables are extensive; this module implements the standard
component formulas used in professional engines (normalized + raw virupas).
Max per component ≈ 60 virupas; total Shadbala max ≈ 360 virupas (6 rupas).
"""

from __future__ import annotations

from typing import Any

from app.core.constants import DEBILITATION, EXALTATION, OWN_SIGNS, SIGN_LORDS
from app.jyotish.dignity import NATURAL_ENEMIES, NATURAL_FRIENDS
from app.jyotish.utils import sign_from_longitude

# Naisargika bala (virupas) — classical fixed values
NAISARGIKA: dict[str, float] = {
    "Sun": 60.0,
    "Moon": 51.43,
    "Venus": 42.85,
    "Jupiter": 34.28,
    "Mercury": 25.70,
    "Mars": 17.14,
    "Saturn": 8.57,
    "Rahu": 12.0,
    "Ketu": 12.0,
}

# Dig Bala: full strength (60) when planet in this house; zero opposite
DIG_FULL_HOUSE: dict[str, int] = {
    "Sun": 10,
    "Mars": 10,
    "Jupiter": 1,
    "Mercury": 1,
    "Saturn": 7,
    "Venus": 4,
    "Moon": 4,
}

# Uchcha / neecha longitudes (approx sign mid exaltation for continuous sthana)
EXALT_DEG: dict[str, float] = {
    "Sun": 10.0,  # Aries 10°
    "Moon": 33.0,  # Taurus 3°
    "Mars": 298.0,  # Capricorn 28°
    "Mercury": 165.0,  # Virgo 15°
    "Jupiter": 95.0,  # Cancer 5°
    "Venus": 357.0,  # Pisces 27°
    "Saturn": 200.0,  # Libra 20°
}


def _norm(x: float) -> float:
    return x % 360.0


def _angle_diff(a: float, b: float) -> float:
    return abs((_norm(a - b) + 180) % 360 - 180)


def sthana_bala(planet: str, longitude: float, house: int) -> dict[str, float]:
    """Positional strength: uchcha + sapta varga proxy + kendradi + drekkana proxy."""
    sign = int(longitude // 30)
    # Uchcha bala: 60 at exaltation degree, 0 at debilitation (180° away)
    exalt = EXALT_DEG.get(planet)
    if exalt is not None:
        dist = _angle_diff(longitude, exalt)
        uchcha = max(0.0, 60.0 * (1.0 - dist / 180.0))
    else:
        uchcha = 30.0

    # Saptavargaja proxy from dignity
    if EXALTATION.get(planet) == sign:
        sapta = 45.0
    elif sign in OWN_SIGNS.get(planet, []):
        sapta = 30.0
    else:
        lord = SIGN_LORDS[sign]
        if planet in NATURAL_FRIENDS and lord in NATURAL_FRIENDS.get(planet, set()):
            sapta = 22.5
        elif planet in NATURAL_ENEMIES and lord in NATURAL_ENEMIES.get(planet, set()):
            sapta = 7.5
        elif DEBILITATION.get(planet) == sign:
            sapta = 3.75
        else:
            sapta = 15.0

    # Kendradi: kendra 60, panaphara 30, apoklima 15 (as contribution unit /4 style)
    if house in {1, 4, 7, 10}:
        kendradi = 60.0
    elif house in {2, 5, 8, 11}:
        kendradi = 30.0
    else:
        kendradi = 15.0

    # Ojhayugmarasyamsa + Kendra etc. collapsed into small Ojha bonus
    ojha = 15.0 if sign % 2 == 0 else 0.0  # odd signs traditionally for male planets — simplified

    total = uchcha + sapta + kendradi * 0.25 + ojha * 0.25
    return {
        "uchcha_bala": round(uchcha, 2),
        "saptavargaja_proxy": round(sapta, 2),
        "kendradi_contribution": round(kendradi * 0.25, 2),
        "ojha_contribution": round(ojha * 0.25, 2),
        "total": round(min(60.0, total * 0.55), 2),  # normalize toward ~60 max
    }


def dig_bala(planet: str, house: int) -> float:
    full = DIG_FULL_HOUSE.get(planet)
    if full is None:
        return 15.0
    # Distance from ideal house in house-count
    dist = min((house - full) % 12, (full - house) % 12)
    return round(max(0.0, 60.0 * (1.0 - dist / 6.0)), 2)


def kala_bala(planet: str, is_day_birth: bool, weekday: int) -> float:
    """Temporal strength — day/night + paksha/weekday proxy."""
    day_strong = {"Sun", "Jupiter", "Venus"}
    night_strong = {"Moon", "Mars", "Saturn"}
    score = 30.0
    if is_day_birth and planet in day_strong:
        score += 20.0
    if not is_day_birth and planet in night_strong:
        score += 20.0
    if planet == "Mercury":
        score += 15.0
    # Weekday lord bonus (0=Mon ... simplified using Python weekday)
    weekday_lords = ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Sun"]
    if weekday_lords[weekday % 7] == planet:
        score += 10.0
    return round(min(60.0, score), 2)


def chesta_bala(planet: str, speed: float, retrograde: bool) -> float:
    if planet in {"Sun", "Moon"}:
        # Luminaries use different chesta; use speed vs mean as proxy
        return round(min(60.0, abs(speed) * 8.0), 2)
    if planet in {"Rahu", "Ketu"}:
        return 40.0 if retrograde else 20.0
    if retrograde:
        return 60.0
    return round(min(60.0, max(5.0, abs(speed) * 25.0)), 2)


def naisargika_bala(planet: str) -> float:
    return NAISARGIKA.get(planet, 15.0)


def drik_bala(planet: str, positions: dict[str, float], house_map: dict[str, int]) -> float:
    """Aspect strength proxy: benefics on kendra/trikona from planet add, malefics subtract."""
    benefics = {"Jupiter", "Venus", "Mercury", "Moon"}
    malefics = {"Saturn", "Mars", "Rahu", "Ketu", "Sun"}
    if planet not in positions:
        return 0.0
    base_house = house_map.get(planet, 1)
    score = 0.0
    for other, _lon in positions.items():
        if other == planet or other in {"Uranus", "Neptune", "Pluto"}:
            continue
        oh = house_map.get(other, 1)
        rel = ((oh - base_house) % 12) + 1
        if rel in {1, 5, 7, 9}:  # conjunction / trine / opposition style houses
            if other in benefics:
                score += 10.0
            elif other in malefics:
                score -= 8.0
    return round(max(-30.0, min(60.0, score + 20.0)), 2)


def compute_shadbala(
    planet: str,
    longitude: float,
    house: int,
    speed: float,
    retrograde: bool,
    positions: dict[str, float],
    house_map: dict[str, int],
    is_day_birth: bool,
    weekday: int,
) -> dict[str, Any]:
    sth = sthana_bala(planet, longitude, house)
    dig = dig_bala(planet, house)
    kala = kala_bala(planet, is_day_birth, weekday)
    chesta = chesta_bala(planet, speed, retrograde)
    nais = naisargika_bala(planet)
    drik = drik_bala(planet, positions, house_map)

    total = sth["total"] + dig + kala + chesta + nais + max(0.0, drik)
    # Required minimums (classical approx in virupas) for "strong"
    required = {
        "Sun": 390,
        "Moon": 360,
        "Mars": 300,
        "Mercury": 420,
        "Jupiter": 390,
        "Venus": 330,
        "Saturn": 300,
    }.get(planet, 300)
    # Our totals are scaled ~0-360; map required similarly
    req_scaled = required / 2.0
    return {
        "unit": "virupa_approx",
        "sthana_bala": sth,
        "dig_bala": dig,
        "kala_bala": kala,
        "chesta_bala": chesta,
        "naisargika_bala": nais,
        "drik_bala": drik,
        "total": round(total, 2),
        "required_approx": round(req_scaled, 2),
        "is_strong": total >= req_scaled,
        "total_normalized": round(min(1.0, total / 360.0), 3),
        "rupa": round(total / 60.0, 3),
        "note": "Parashari Shadbala component formulas (engineering-grade approx).",
    }
