"""Vargas / divisional charts D1–D60 (standard Parashari mappings)."""

from __future__ import annotations

from app.core.constants import VARGAS


def _varga_sign(longitude: float, division: int, mapping: str) -> int:
    """Return 0-based sign index for a varga longitude mapping."""
    lon = longitude % 360.0
    sign = int(lon // 30)
    part = lon % 30.0
    segment = int(part * division / 30.0)  # 0 .. division-1

    if mapping == "sequential":
        # D1-style: each segment advances one sign from rasi
        return (sign + segment) % 12

    if mapping == "d2":
        # Hora: odd signs → Sun (Leo=4) for first half, Moon (Cancer=3) second;
        # even signs reverse. Simplified classic.
        first_half = part < 15.0
        if sign % 2 == 0:  # odd signs (0=Aries)
            return 4 if first_half else 3
        return 3 if first_half else 4

    if mapping == "d3":
        # Drekkana: 0-10 same, 10-20 5th from it, 20-30 9th
        if segment == 0:
            return sign
        if segment == 1:
            return (sign + 4) % 12
        return (sign + 8) % 12

    if mapping == "d4":
        # Chaturthamsha: 0-7.5 same, then 4th, 7th, 10th
        offsets = [0, 3, 6, 9]
        return (sign + offsets[segment]) % 12

    if mapping == "d7":
        # Saptamsha: odd from same, even from 7th
        start = sign if sign % 2 == 0 else (sign + 6) % 12
        return (start + segment) % 12

    if mapping == "d9":
        # Navamsa: movable from same, fixed from 9th, dual from 5th
        if sign % 3 == 0:  # movable
            start = sign
        elif sign % 3 == 1:  # fixed
            start = (sign + 8) % 12
        else:  # dual
            start = (sign + 4) % 12
        return (start + segment) % 12

    if mapping == "d10":
        # Dasamsha: odd from same, even from 9th
        start = sign if sign % 2 == 0 else (sign + 8) % 12
        return (start + segment) % 12

    if mapping == "d12":
        return (sign + segment) % 12

    if mapping == "d16":
        if sign % 3 == 0:
            start = 0  # Aries
        elif sign % 3 == 1:
            start = 4  # Leo
        else:
            start = 8  # Sagittarius
        return (start + segment) % 12

    if mapping == "d20":
        if sign % 3 == 0:
            start = 0
        elif sign % 3 == 1:
            start = 8
        else:
            start = 4
        return (start + segment) % 12

    if mapping == "d24":
        start = 4 if sign % 2 == 0 else 3  # Leo / Cancer
        return (start + segment) % 12

    if mapping == "d27":
        start = (sign * 3) % 12  # simplified nakshatramsha start
        return (start + segment) % 12

    if mapping == "d30":
        # Trimshamsha (simplified classical by degrees)
        d = part
        if sign % 2 == 0:  # odd signs
            if d < 5:
                return 0  # Mars-Aries
            if d < 10:
                return 10  # Saturn-Aquarius
            if d < 18:
                return 8  # Jupiter
            if d < 25:
                return 2  # Mercury
            return 6  # Venus
        if d < 5:
            return 1  # Venus-Taurus
        if d < 12:
            return 5  # Mercury
        if d < 20:
            return 11  # Jupiter
        if d < 25:
            return 9  # Saturn
        return 7  # Mars-Scorpio

    if mapping == "d60":
        return (sign + segment) % 12

    # Default sequential for remaining (D5, D6, D8, D11, D40, D45, …)
    return (sign + segment) % 12


_MAPPING: dict[str, str] = {
    "D1": "sequential",
    "D2": "d2",
    "D3": "d3",
    "D4": "d4",
    "D7": "d7",
    "D9": "d9",
    "D10": "d10",
    "D12": "d12",
    "D16": "d16",
    "D20": "d20",
    "D24": "d24",
    "D27": "d27",
    "D30": "d30",
    "D60": "d60",
}


def varga_longitude(longitude: float, varga: str) -> float:
    """Approximate varga longitude as sign_start + scaled degree-in-segment."""
    key = varga.upper()
    division = VARGAS[key]
    if division == 1:
        return longitude % 360.0

    mapping = _MAPPING.get(key, "sequential")
    lon = longitude % 360.0
    part = lon % 30.0
    segment = int(part * division / 30.0)
    seg_size = 30.0 / division
    within = (part - segment * seg_size) / seg_size * 30.0
    sign_idx = _varga_sign(lon, division, mapping)
    return sign_idx * 30.0 + within


def all_vargas(longitude: float) -> dict[str, float]:
    return {name: varga_longitude(longitude, name) for name in VARGAS}
