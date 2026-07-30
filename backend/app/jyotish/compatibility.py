"""Advanced chart compatibility beyond Ashtakoot (modern composite layer)."""

from __future__ import annotations

from dataclasses import dataclass

from app.core.constants import SIGN_LORDS, SIGNS
from app.jyotish.utils import sign_from_longitude


def _sign(lon: float) -> int:
    return sign_from_longitude(lon).sign_index


def _house(planet_lon: float, lagna_lon: float) -> int:
    return ((_sign(planet_lon) - _sign(lagna_lon)) % 12) + 1


def _aspect_harmony(lon_a: float, lon_b: float) -> tuple[float, str]:
    """Soft score from sign relationship between two longitudes."""
    diff = abs(_sign(lon_a) - _sign(lon_b)) % 12
    diff = min(diff, 12 - diff)
    if diff == 0:
        return 1.0, "conjunction by sign"
    if diff == 6:
        return 0.35, "opposition by sign"
    if diff in {3, 4}:  # square-ish / trine-ish in sign counting
        return (0.55 if diff == 3 else 0.9), ("4/10 link" if diff == 3 else "trinal link")
    if diff in {2, 5}:
        return 0.7, "sextile-like / complementary"
    return 0.6, f"sign distance {diff}"


@dataclass(slots=True)
class DimensionScore:
    key: str
    label: str
    score: float  # 0–100
    band: str
    detail: str
    factors: list[str]


def _band(score: float) -> str:
    if score >= 75:
        return "strong"
    if score >= 55:
        return "good"
    if score >= 40:
        return "mixed"
    return "challenging"


def _clamp(x: float) -> float:
    return round(max(0.0, min(100.0, x)), 1)


def _moon_compat(boy: dict, girl: dict) -> DimensionScore:
    bm, gm = boy["positions"]["Moon"], girl["positions"]["Moon"]
    base, rel = _aspect_harmony(bm, gm)
    # Emotional ease if Moons in friendly elements
    elements = [0, 1, 2, 3]  # fire earth air water by sign%4
    be, ge = _sign(bm) % 4, _sign(gm) % 4
    elem_bonus = 0.15 if be == ge else (0.08 if {be, ge} in [{0, 2}, {1, 3}] else 0)
    score = _clamp((base + elem_bonus) * 85)
    return DimensionScore(
        key="moon",
        label="Moon Compatibility",
        score=score,
        band=_band(score),
        detail=f"Moon signs {SIGNS[_sign(bm)]}–{SIGNS[_sign(gm)]} ({rel}).",
        factors=[
            f"Boy Moon: {SIGNS[_sign(bm)]}",
            f"Girl Moon: {SIGNS[_sign(gm)]}",
            rel,
        ],
    )


def _venus_compat(boy: dict, girl: dict) -> DimensionScore:
    bv, gv = boy["positions"]["Venus"], girl["positions"]["Venus"]
    base, rel = _aspect_harmony(bv, gv)
    # Each Venus on other's 7th/5th helps affection
    bonus = 0.0
    factors = [rel]
    for label, chart, other_v in (
        ("Boy Venus→Girl Lagna", boy, girl["ascendant"]),
        ("Girl Venus→Boy Lagna", girl, boy["ascendant"]),
    ):
        h = _house(chart["positions"]["Venus"], other_v)
        if h in {1, 5, 7}:
            bonus += 0.08
            factors.append(f"{label} house {h}")
    score = _clamp((base + bonus) * 88)
    return DimensionScore(
        key="venus",
        label="Venus Compatibility",
        score=score,
        band=_band(score),
        detail="Affection, aesthetics, and romantic chemistry (traditional Venus links).",
        factors=[
            f"Boy Venus: {SIGNS[_sign(bv)]}",
            f"Girl Venus: {SIGNS[_sign(gv)]}",
            *factors,
        ],
    )


def _mars_compat(boy: dict, girl: dict) -> DimensionScore:
    bm, gm = boy["positions"]["Mars"], girl["positions"]["Mars"]
    base, rel = _aspect_harmony(bm, gm)
    # Manglik clash caution
    boy_mh = _house(bm, boy["ascendant"])
    girl_mh = _house(gm, girl["ascendant"])
    boy_m = boy_mh in {1, 4, 7, 8, 12}
    girl_m = girl_mh in {1, 4, 7, 8, 12}
    factors = [rel, f"Boy Mars H{boy_mh}", f"Girl Mars H{girl_mh}"]
    penalty = 0.0
    if boy_m != girl_m:
        penalty = 0.18
        factors.append("Uneven Manglik pattern — review carefully")
    elif boy_m and girl_m:
        factors.append("Both Manglik-pattern — often considered balancing")
        base += 0.05
    score = _clamp((base - penalty) * 86)
    return DimensionScore(
        key="mars",
        label="Mars Compatibility",
        score=score,
        band=_band(score),
        detail="Drive, conflict style, and Manglik-pattern balance.",
        factors=factors,
    )


def _emotional(boy: dict, girl: dict, moon: DimensionScore) -> DimensionScore:
    # Moon + 4th lords
    b4 = SIGN_LORDS[(_sign(boy["ascendant"]) + 3) % 12]
    g4 = SIGN_LORDS[(_sign(girl["ascendant"]) + 3) % 12]
    factors = [f"4th lords {b4}/{g4}", f"Moon band: {moon.band}"]
    score = moon.score
    if b4 == g4:
        score = _clamp(score + 8)
        factors.append("Shared 4th-lord theme")
    return DimensionScore(
        key="emotional",
        label="Emotional Compatibility",
        score=score,
        band=_band(score),
        detail="Home/emotional comfort via Moon and 4th-house symbolism.",
        factors=factors,
    )


def _communication(boy: dict, girl: dict) -> DimensionScore:
    bme, gme = boy["positions"]["Mercury"], girl["positions"]["Mercury"]
    base, rel = _aspect_harmony(bme, gme)
    # 3rd house link
    bonus = 0.0
    for chart, other in ((boy, girl), (girl, boy)):
        h = _house(chart["positions"]["Mercury"], other["ascendant"])
        if h in {1, 3, 7}:
            bonus += 0.06
    score = _clamp((base + bonus) * 90)
    return DimensionScore(
        key="communication",
        label="Communication",
        score=score,
        band=_band(score),
        detail=f"Mercury signs {SIGNS[_sign(bme)]}–{SIGNS[_sign(gme)]} ({rel}).",
        factors=[rel, f"Boy Mercury H{_house(bme, boy['ascendant'])}", f"Girl Mercury H{_house(gme, girl['ascendant'])}"],
    )


def _finance(boy: dict, girl: dict) -> DimensionScore:
    # 2nd/11th lords + Venus/Jupiter
    score = 50.0
    factors = []
    for label, chart in (("Boy", boy), ("Girl", girl)):
        lagna = chart["ascendant"]
        second_lord = SIGN_LORDS[_sign(lagna)]
        # use 2nd and 11th
        l2 = SIGN_LORDS[(_sign(lagna) + 1) % 12]
        l11 = SIGN_LORDS[(_sign(lagna) + 10) % 12]
        for lord in {l2, l11}:
            lon = chart["positions"].get(lord)
            if lon is None:
                continue
            h = _house(lon, lagna)
            if h in {1, 2, 5, 9, 10, 11}:
                score += 4
                factors.append(f"{label} {lord} supportive in H{h}")
            elif h in {6, 8, 12}:
                score -= 3
                factors.append(f"{label} {lord} stressed in H{h}")
    # Mutual Venus-Jupiter
    v_h, _ = _aspect_harmony(boy["positions"]["Venus"], girl["positions"]["Jupiter"])
    j_h, _ = _aspect_harmony(boy["positions"]["Jupiter"], girl["positions"]["Venus"])
    score += (v_h + j_h) * 10
    factors.append("Venus–Jupiter cross links considered")
    score = _clamp(score)
    return DimensionScore(
        key="finance",
        label="Finance",
        score=score,
        band=_band(score),
        detail="Resource harmony from 2nd/11th lords and Venus–Jupiter themes.",
        factors=factors[:6],
    )


def _children(boy: dict, girl: dict) -> DimensionScore:
    score = 55.0
    factors = []
    for label, chart in (("Boy", boy), ("Girl", girl)):
        lagna = chart["ascendant"]
        fifth_lord = SIGN_LORDS[(_sign(lagna) + 4) % 12]
        lon = chart["positions"].get(fifth_lord)
        jup = chart["positions"]["Jupiter"]
        if lon is not None:
            h = _house(lon, lagna)
            if h in {1, 4, 5, 7, 9, 11}:
                score += 6
                factors.append(f"{label} 5th lord {fifth_lord} in H{h}")
            elif h in {6, 8, 12}:
                score -= 4
                factors.append(f"{label} 5th lord stressed in H{h}")
        jh = _house(jup, lagna)
        if jh in {1, 5, 7, 9}:
            score += 4
            factors.append(f"{label} Jupiter in H{jh}")
    score = _clamp(score)
    return DimensionScore(
        key="children",
        label="Children",
        score=score,
        band=_band(score),
        detail="5th house / Jupiter traditional fertility & progeny indicators.",
        factors=factors,
    )


def _career(boy: dict, girl: dict) -> DimensionScore:
    score = 52.0
    factors = []
    for label, chart in (("Boy", boy), ("Girl", girl)):
        lagna = chart["ascendant"]
        tenth_lord = SIGN_LORDS[(_sign(lagna) + 9) % 12]
        lon = chart["positions"].get(tenth_lord)
        if lon is None:
            continue
        h = _house(lon, lagna)
        if h in {1, 2, 9, 10, 11}:
            score += 6
            factors.append(f"{label} 10th lord strong in H{h}")
        elif h in {6, 8, 12}:
            score -= 3
            factors.append(f"{label} 10th lord in H{h}")
    # Synastry: one person's Saturn on other's 10th can feel heavy
    for a, b, lab in (
        (boy, girl, "Boy Saturn→Girl"),
        (girl, boy, "Girl Saturn→Boy"),
    ):
        h = _house(a["positions"]["Saturn"], b["ascendant"])
        if h == 10:
            score -= 5
            factors.append(f"{lab} 10th — duty-heavy career overlay")
        if h in {1, 7}:
            score += 2
    score = _clamp(score)
    return DimensionScore(
        key="career",
        label="Career",
        score=score,
        band=_band(score),
        detail="Mutual support for vocation via 10th-lord and Saturn overlays.",
        factors=factors[:6],
    )


def _physical(boy: dict, girl: dict, mars: DimensionScore, venus: DimensionScore) -> DimensionScore:
    score = _clamp(0.55 * venus.score + 0.45 * mars.score)
    return DimensionScore(
        key="physical",
        label="Physical Compatibility",
        score=score,
        band=_band(score),
        detail="Composite of Venus (attraction) and Mars (energy) links.",
        factors=[f"Venus {venus.band}", f"Mars {mars.band}"],
    )


def _family(boy: dict, girl: dict) -> DimensionScore:
    score = 50.0
    factors = []
    # 4th and 9th / elders
    for label, chart in (("Boy", boy), ("Girl", girl)):
        lagna = chart["ascendant"]
        for house, name in ((4, "4th"), (9, "9th")):
            lord = SIGN_LORDS[(_sign(lagna) + house - 1) % 12]
            lon = chart["positions"].get(lord)
            if lon is None:
                continue
            h = _house(lon, lagna)
            if h in {1, 4, 5, 9, 10, 11}:
                score += 4
                factors.append(f"{label} {name} lord supportive")
            elif h in {6, 8, 12}:
                score -= 3
                factors.append(f"{label} {name} lord stressed")
    # Moon on each other's 4th
    for a, b, lab in ((boy, girl, "Boy Moon→Girl"), (girl, boy, "Girl Moon→Boy")):
        h = _house(a["positions"]["Moon"], b["ascendant"])
        if h in {4, 7}:
            score += 6
            factors.append(f"{lab} H{h}")
    score = _clamp(score)
    return DimensionScore(
        key="family",
        label="Family Compatibility",
        score=score,
        band=_band(score),
        detail="4th/9th house comfort with family & elders (traditional reading).",
        factors=factors[:6],
    )


def _attachment(boy: dict, girl: dict, moon: DimensionScore, venus: DimensionScore) -> DimensionScore:
    score = _clamp(0.6 * moon.score + 0.4 * venus.score)
    factors = [f"Moon {moon.band}", f"Venus {venus.band}"]
    # Moon-Venus cross
    for a, b, lab in ((boy, girl, "Boy Moon→Girl Venus sign"), (girl, boy, "Girl Moon→Boy Venus")):
        if _sign(a["positions"]["Moon"]) == _sign(b["positions"]["Venus"]):
            score = _clamp(score + 8)
            factors.append(f"{lab} resonance")
    return DimensionScore(
        key="attachment",
        label="Attachment Style",
        score=score,
        band=_band(score),
        detail="Emotional bonding style via Moon-Venus synastry (traditional symbolism).",
        factors=factors,
    )


def _lifestyle(boy: dict, girl: dict) -> DimensionScore:
    score = 52.0
    factors = []
    # Ascendant element compatibility
    be, ge = _sign(boy["ascendant"]) % 4, _sign(girl["ascendant"]) % 4
    if be == ge:
        score += 18
        factors.append("Same lagna element")
    elif {be, ge} in [{0, 2}, {1, 3}]:
        score += 10
        factors.append("Complementary lagna elements")
    # Saturn lifestyle pace
    bs, gs = _house(boy["positions"]["Saturn"], boy["ascendant"]), _house(
        girl["positions"]["Saturn"], girl["ascendant"]
    )
    if abs(bs - gs) <= 2 or abs(bs - gs) >= 10:
        score += 8
        factors.append("Similar Saturn lifestyle pace")
    score = _clamp(score)
    return DimensionScore(
        key="lifestyle",
        label="Lifestyle",
        score=score,
        band=_band(score),
        detail="Daily-life rhythm via Lagna element and Saturn pace.",
        factors=factors,
    )


def _conflict(boy: dict, girl: dict, mars: DimensionScore) -> DimensionScore:
    score = _clamp(100 - abs(mars.score - 55) * 0.8)
    factors = [f"Mars band {mars.band}"]
    # Mars on each other's Moon — friction
    for a, b, lab in ((boy, girl, "Boy Mars→Girl Moon"), (girl, boy, "Girl Mars→Boy Moon")):
        if _sign(a["positions"]["Mars"]) == _sign(b["positions"]["Moon"]):
            score = _clamp(score - 12)
            factors.append(f"{lab} friction flag")
    # Mercury communication buffer
    base, rel = _aspect_harmony(boy["positions"]["Mercury"], girl["positions"]["Mercury"])
    score = _clamp(score + base * 10)
    factors.append(rel)
    return DimensionScore(
        key="conflict",
        label="Conflict Style",
        score=score,
        band=_band(score),
        detail="How friction shows up — Mars/Moon heat vs Mercury mediation.",
        factors=factors,
    )


def advanced_compatibility(boy: dict, girl: dict) -> dict:
    moon = _moon_compat(boy, girl)
    venus = _venus_compat(boy, girl)
    mars = _mars_compat(boy, girl)
    dims = [
        moon,
        venus,
        mars,
        _emotional(boy, girl, moon),
        _communication(boy, girl),
        _finance(boy, girl),
        _children(boy, girl),
        _career(boy, girl),
        _physical(boy, girl, mars, venus),
        _family(boy, girl),
        _attachment(boy, girl, moon, venus),
        _lifestyle(boy, girl),
        _conflict(boy, girl, mars),
    ]
    overall = _clamp(sum(d.score for d in dims) / len(dims))
    why = [
        f"{d.label}: {d.score} ({d.band}) — {d.detail}"
        for d in sorted(dims, key=lambda x: x.score)
    ]
    return {
        "overall_score": overall,
        "overall_band": _band(overall),
        "dimensions": [
            {
                "key": d.key,
                "label": d.label,
                "score": d.score,
                "band": d.band,
                "detail": d.detail,
                "factors": d.factors,
                "evidence_why": d.factors,
            }
            for d in dims
        ],
        "why_summary": why,
        "note": (
            "Modern composite layer built on classical house/planet symbolism. "
            "Not a scientifically validated prediction."
        ),
    }
