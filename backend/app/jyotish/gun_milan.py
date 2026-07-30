"""Ashtakoot / Gun Milan — 36 guna matching."""

from __future__ import annotations

from dataclasses import dataclass

from app.core.constants import SIGNS
from app.jyotish.utils import nakshatra_from_longitude, sign_from_longitude

# Varna by sign element grouping (classic mapping by Moon sign)
VARNA_BY_SIGN = [
    3,  # Aries — Kshatriya
    2,  # Taurus — Vaishya
    1,  # Gemini — Shudra
    4,  # Cancer — Brahmin
    3,
    2,
    1,
    4,
    3,
    2,
    1,
    4,
]

# Vashya groups by Moon sign (simplified)
# 1=Chatushpada, 2=Manava, 3=Jalachar, 4=Vanacara, 5=Keeta
VASHYA_BY_SIGN = [1, 1, 2, 3, 2, 2, 2, 5, 1, 1, 2, 3]

# Yoni of each nakshatra (0-13 animal pairs)
YONI = [
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13,
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,
]

YONI_MALE = [True, False, True, False, True, False, True, False, True, False, True, False, True, False]

# Gana: 0=Deva, 1=Manushya, 2=Rakshasa
GANA = [
    0, 1, 2, 1, 0, 2, 0, 0, 2, 2, 1, 1, 0, 2, 0, 2, 0, 2, 2, 1, 1, 0, 2, 2, 1, 1, 0
]

# Nadi: 0=Adi, 1=Madhya, 2=Antya
NADI = [
    0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2
]

# Graha maitri table (planet friendship scores 0-5) keyed by sign lord index
# Lords: Mars Venus Mercury Moon Sun Mercury Venus Mars Jupiter Saturn Saturn Jupiter
SIGN_LORD_PLANET = [0, 1, 2, 3, 4, 2, 1, 0, 5, 6, 6, 5]  # index into planet matrix

# Simplified friend matrix max 5
FRIEND_MATRIX = [
    # Mars Venus Merc Moon Sun Jup Sat
    [5, 3, 3, 4, 5, 5, 1],  # Mars
    [3, 5, 5, 3, 1, 3, 5],  # Venus
    [3, 5, 5, 4, 4, 1, 3],  # Mercury
    [4, 3, 4, 5, 5, 4, 1],  # Moon
    [5, 1, 4, 5, 5, 5, 1],  # Sun
    [5, 3, 1, 4, 5, 5, 1],  # Jupiter
    [1, 5, 3, 1, 1, 1, 5],  # Saturn
]


@dataclass(slots=True)
class KootaScore:
    name: str
    obtained: float
    maximum: float
    notes: str


@dataclass(slots=True)
class GunMilanResult:
    total: float
    maximum: float
    percentage: float
    verdict: str
    kootas: list[KootaScore]
    boy_nakshatra: str
    girl_nakshatra: str
    boy_rasi: str
    girl_rasi: str


def _varna_score(boy_sign: int, girl_sign: int) -> KootaScore:
    b, g = VARNA_BY_SIGN[boy_sign], VARNA_BY_SIGN[girl_sign]
    ok = b >= g
    return KootaScore("Varna", 1.0 if ok else 0.0, 1.0, "Boy varna >= Girl varna")


def _vashya_score(boy_sign: int, girl_sign: int) -> KootaScore:
    if boy_sign == girl_sign:
        pts = 2.0
    elif VASHYA_BY_SIGN[boy_sign] == VASHYA_BY_SIGN[girl_sign]:
        pts = 1.0
    else:
        pts = 0.5
    return KootaScore("Vashya", pts, 2.0, "Control/compatibility by Moon sign group")


def _tara_score(boy_nak: int, girl_nak: int) -> KootaScore:
    # Count from girl to boy
    diff = (boy_nak - girl_nak) % 27
    tara = (diff % 9) + 1
    auspicious = tara in {1, 2, 3, 4, 6, 8}
    return KootaScore("Tara", 3.0 if auspicious else 0.0, 3.0, f"Tara number {tara}")


def _yoni_score(boy_nak: int, girl_nak: int) -> KootaScore:
    yb, yg = YONI[boy_nak], YONI[girl_nak]
    if yb == yg:
        # same yoni — check male/female pairing ideally opposite gender of same animal
        pts = 4.0 if YONI_MALE[yb % 14] != YONI_MALE[yg % 14] else 2.0
        # same index always same animal; classical full 4 when complementary
        pts = 4.0
    else:
        # enemy yoni pairs (simplified)
        enemies = {(0, 5), (1, 7), (2, 9), (3, 10), (4, 8), (6, 11), (12, 13)}
        pair = tuple(sorted((yb, yg)))
        pts = 0.0 if pair in enemies else 2.0
    return KootaScore("Yoni", pts, 4.0, "Animal yoni matching")


def _graha_maitri(boy_sign: int, girl_sign: int) -> KootaScore:
    pb = SIGN_LORD_PLANET[boy_sign]
    pg = SIGN_LORD_PLANET[girl_sign]
    pts = float(FRIEND_MATRIX[pb][pg])
    # normalize classic max is 5
    return KootaScore("Graha Maitri", min(pts, 5.0), 5.0, "Moon-sign lord friendship")


def _gana_score(boy_nak: int, girl_nak: int) -> KootaScore:
    gb, gg = GANA[boy_nak], GANA[girl_nak]
    if gb == gg:
        pts = 6.0
    elif {gb, gg} == {0, 1}:
        pts = 5.0
    elif {gb, gg} == {1, 2}:
        pts = 1.0
    else:  # Deva-Rakshasa
        pts = 0.0
    return KootaScore("Gana", pts, 6.0, "Deva / Manushya / Rakshasa")


def _bhakut_score(boy_sign: int, girl_sign: int) -> KootaScore:
    diff = (girl_sign - boy_sign) % 12
    # Auspicious: 1/1, 1/7, 2/12, 3/11, 4/10, 5/9, 6/8 patterns — classic uses specific pairs
    good = diff in {0, 3, 4, 7, 10, 11}
    # 6/8 (diff 5 or 7) is often dosha — treat carefully
    if diff in {5, 7}:
        pts = 0.0
    elif good:
        pts = 7.0
    else:
        pts = 0.0
    return KootaScore("Bhakut", pts, 7.0, f"Rasi difference {diff}")


def _nadi_score(boy_nak: int, girl_nak: int) -> KootaScore:
    same = NADI[boy_nak] == NADI[girl_nak]
    return KootaScore(
        "Nadi",
        0.0 if same else 8.0,
        8.0,
        "Same nadi is dosha" if same else "Different nadi — full points",
    )


def _verdict(total: float) -> str:
    if total >= 32:
        return "Excellent"
    if total >= 24:
        return "Good"
    if total >= 18:
        return "Average — review with full charts"
    return "Low — classical texts advise caution; full chart matching required"


def gun_milan(boy_moon_lon: float, girl_moon_lon: float) -> GunMilanResult:
    b_sign = sign_from_longitude(boy_moon_lon).sign_index
    g_sign = sign_from_longitude(girl_moon_lon).sign_index
    b_nak = nakshatra_from_longitude(boy_moon_lon)
    g_nak = nakshatra_from_longitude(girl_moon_lon)

    kootas = [
        _varna_score(b_sign, g_sign),
        _vashya_score(b_sign, g_sign),
        _tara_score(b_nak.index, g_nak.index),
        _yoni_score(b_nak.index, g_nak.index),
        _graha_maitri(b_sign, g_sign),
        _gana_score(b_nak.index, g_nak.index),
        _bhakut_score(b_sign, g_sign),
        _nadi_score(b_nak.index, g_nak.index),
    ]
    total = sum(k.obtained for k in kootas)
    maximum = 36.0
    return GunMilanResult(
        total=total,
        maximum=maximum,
        percentage=round(total / maximum * 100, 2),
        verdict=_verdict(total),
        kootas=kootas,
        boy_nakshatra=b_nak.name,
        girl_nakshatra=g_nak.name,
        boy_rasi=SIGNS[b_sign],
        girl_rasi=SIGNS[g_sign],
    )
