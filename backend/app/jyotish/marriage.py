"""Marriage analysis rule engine (traditional Vedic indicators).

Outputs are classical interpretive signals — not scientifically proven predictions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from app.core.constants import (
    EXALTATION,
    OWN_SIGNS,
    SIGN_LORDS,
    SIGNS,
    VIMSHOTTARI_ORDER,
)
from app.jyotish.dasha import antar_dashas, vimshottari_mahadashas
from app.jyotish.utils import nakshatra_from_longitude, sign_from_longitude
from app.jyotish.vargas import varga_longitude


def _sign(lon: float) -> int:
    return sign_from_longitude(lon).sign_index


def _house(planet_lon: float, lagna_lon: float) -> int:
    return ((_sign(planet_lon) - _sign(lagna_lon)) % 12) + 1


def _lord_of_house(lagna_lon: float, house: int) -> str:
    sign = (_sign(lagna_lon) + house - 1) % 12
    return SIGN_LORDS[sign]


@dataclass(slots=True)
class Indicator:
    key: str
    label: str
    present: bool
    weight: float
    detail: str


@dataclass
class MarriageAnalysis:
    seventh_house: dict
    venus: dict
    jupiter: dict
    navamsa: dict
    karakas: dict
    timing_windows: list[dict] = field(default_factory=list)
    love_marriage: dict = field(default_factory=dict)
    spouse_profile: dict = field(default_factory=dict)
    indicators: list[Indicator] = field(default_factory=list)
    summary: dict = field(default_factory=dict)


def _planet_row(chart: dict, name: str) -> dict:
    return next(p for p in chart["planets"] if p["name"] == name)


def _navamsa_map(positions: dict[str, float], lagna: float) -> dict:
    bodies = {"Lagna": lagna, **positions}
    out = {}
    for name, lon in bodies.items():
        if name in {"Uranus", "Neptune", "Pluto"}:
            continue
        vlon = varga_longitude(lon, "D9")
        sp = sign_from_longitude(vlon)
        out[name] = {
            "longitude": round(vlon, 4),
            "sign": sp.sign,
            "sign_index": sp.sign_index,
            "lord": SIGN_LORDS[sp.sign_index],
        }
    return out


def _char_karakas(positions: dict[str, float]) -> dict:
    """Atmakaraka / Darakaraka from classic 7 / 8 chara karaka longitudes in sign."""
    # Degree in sign descending → AK highest, DK lowest among eligible
    eligible = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    # Include Rahu in some schools — we keep 7-karaka Parashara style
    ranked = sorted(
        ((name, positions[name] % 30.0) for name in eligible if name in positions),
        key=lambda x: x[1],
        reverse=True,
    )
    if not ranked:
        return {}
    return {
        "atmakaraka": {"planet": ranked[0][0], "degree_in_sign": round(ranked[0][1], 4)},
        "darakaraka": {
            "planet": ranked[-1][0],
            "degree_in_sign": round(ranked[-1][1], 4),
        },
        "ranking": [
            {"planet": n, "degree_in_sign": round(d, 4)} for n, d in ranked
        ],
    }


def _upapada_lagna(lagna: float, positions: dict[str, float]) -> dict:
    """UL from Arudha of 12th (simplified Jaimini-style)."""
    # 12th lord from Lagna
    twelfth_sign = (_sign(lagna) + 11) % 12
    lord = SIGN_LORDS[twelfth_sign]
    lord_lon = positions.get(lord)
    if lord_lon is None:
        return {"sign": SIGNS[twelfth_sign], "lord": lord, "note": "lord position missing"}
    # Count from 12th sign to lord's sign, same count from lord → UL
    lord_sign = _sign(lord_lon)
    count = (lord_sign - twelfth_sign) % 12
    ul_sign = (lord_sign + count) % 12
    return {
        "sign": SIGNS[ul_sign],
        "sign_index": ul_sign,
        "lord": lord,
        "method": "Arudha of 12th (simplified)",
    }


def marriage_timing_windows(
    moon_lon: float,
    birth_utc: datetime,
    lagna: float,
    positions: dict[str, float],
    years_ahead: int = 20,
) -> list[dict]:
    """Highlight dasha periods classically linked to marriage themes."""
    seventh_lord = _lord_of_house(lagna, 7)
    venus = "Venus"
    jupiter = "Jupiter"
    relevant = {seventh_lord, venus, jupiter, "Moon", "Rahu"}
    mahas = vimshottari_mahadashas(moon_lon, birth_utc, cycles=2)
    windows: list[dict] = []
    horizon = birth_utc.year + years_ahead + 5

    for maha in mahas:
        if maha.start.year > horizon:
            break
        antars = antar_dashas(maha)
        for antar in antars:
            if antar.start.year > birth_utc.year + years_ahead:
                continue
            if antar.end.year < birth_utc.year + 16:
                continue
            score = 0
            reasons = []
            if maha.lord in relevant:
                score += 2
                reasons.append(f"MD {maha.lord}")
            if antar.lord in relevant:
                score += 2
                reasons.append(f"AD {antar.lord}")
            # Double weight if 7th lord involved
            if seventh_lord in {maha.lord, antar.lord}:
                score += 1
                reasons.append("7th lord period")
            if score >= 3:
                windows.append(
                    {
                        "start": antar.start.isoformat(),
                        "end": antar.end.isoformat(),
                        "mahadasha": maha.lord,
                        "antardasha": antar.lord,
                        "score": score,
                        "reasons": reasons,
                        "label": "Marriage-sensitive window (traditional)",
                    }
                )
    windows.sort(key=lambda w: (-w["score"], w["start"]))
    return windows[:12]


def love_marriage_indicators(
    lagna: float,
    positions: dict[str, float],
    navamsa: dict,
) -> dict:
    """Traditional signals often cited for love / inter-caste / foreign themes."""
    indicators: list[Indicator] = []

    fifth = _house(positions.get("Venus", 0), lagna) if "Venus" in positions else None
    venus_h = _house(positions["Venus"], lagna) if "Venus" in positions else None
    mars_h = _house(positions["Mars"], lagna) if "Mars" in positions else None
    rahu_h = _house(positions["Rahu"], lagna) if "Rahu" in positions else None
    moon_h = _house(positions["Moon"], lagna) if "Moon" in positions else None

    # Venus/Mars influence on 5th/7th
    fifth_sign = (_sign(lagna) + 4) % 12
    seventh_sign = (_sign(lagna) + 6) % 12
    for planet, lon in positions.items():
        if planet not in {"Venus", "Mars", "Rahu", "Moon", "Mercury"}:
            continue
        s = _sign(lon)
        if s in {fifth_sign, seventh_sign}:
            indicators.append(
                Indicator(
                    key=f"{planet.lower()}_on_5_7",
                    label=f"{planet} influences 5th/7th sign",
                    present=True,
                    weight=1.2,
                    detail=f"{planet} in {SIGNS[s]} (5th/7th from Lagna by sign).",
                )
            )

    # Rahu in 5/7/9 — often cited for unconventional / foreign themes
    if rahu_h in {5, 7, 9, 12}:
        indicators.append(
            Indicator(
                key="rahu_unconventional",
                label="Rahu in 5/7/9/12",
                present=True,
                weight=1.5,
                detail=f"Rahu in house {rahu_h} — classical unconventional/foreign spouse theme.",
            )
        )

    # Venus-Mars association
    if "Venus" in positions and "Mars" in positions:
        same = _sign(positions["Venus"]) == _sign(positions["Mars"])
        indicators.append(
            Indicator(
                key="venus_mars",
                label="Venus-Mars association",
                present=same,
                weight=1.3 if same else 0,
                detail="Same-sign Venus-Mars (passion / assertive affection theme).",
            )
        )

    # 5th lord in 7th or vice versa
    fifth_lord = _lord_of_house(lagna, 5)
    seventh_lord = _lord_of_house(lagna, 7)
    if fifth_lord in positions and seventh_lord in positions:
        fl_h = _house(positions[fifth_lord], lagna)
        sl_h = _house(positions[seventh_lord], lagna)
        exchangeish = fl_h == 7 or sl_h == 5
        indicators.append(
            Indicator(
                key="5_7_link",
                label="5th–7th lord link",
                present=exchangeish,
                weight=1.4 if exchangeish else 0,
                detail=f"5th lord in H{fl_h}, 7th lord in H{sl_h}.",
            )
        )

    # Navamsa: Venus/Rahu in D9 7th
    d9_lagna = navamsa.get("Lagna", {}).get("sign_index")
    if d9_lagna is not None:
        for p in ("Venus", "Rahu", "Mars"):
            row = navamsa.get(p)
            if not row:
                continue
            h = ((row["sign_index"] - d9_lagna) % 12) + 1
            if h in {5, 7}:
                indicators.append(
                    Indicator(
                        key=f"d9_{p.lower()}_5_7",
                        label=f"D9 {p} in 5/7",
                        present=True,
                        weight=1.1,
                        detail=f"{p} in Navamsa house {h}.",
                    )
                )

    present = [i for i in indicators if i.present]
    score = min(100.0, round(sum(i.weight for i in present) / 8.0 * 100, 1))

    foreign = any(i.key in {"rahu_unconventional"} or "Rahu" in i.label for i in present)
    long_distance = rahu_h in {3, 7, 9, 12} if rahu_h else False
    inter_caste = any(i.key in {"rahu_unconventional", "5_7_link", "venus_mars"} for i in present)

    return {
        "probability_score": score,
        "band": (
            "higher traditional signals"
            if score >= 55
            else "mixed signals"
            if score >= 30
            else "fewer classic love-marriage signals"
        ),
        "themes": {
            "love_marriage_tendency": score >= 40,
            "inter_caste_tendency": inter_caste,
            "long_distance_tendency": long_distance,
            "foreign_spouse_tendency": foreign or long_distance,
        },
        "indicators": [
            {
                "key": i.key,
                "label": i.label,
                "present": i.present,
                "weight": i.weight,
                "detail": i.detail,
            }
            for i in indicators
        ],
        "note": (
            "These are traditional Jyotish indicators only — not certainty, "
            "and not a scientifically validated prediction."
        ),
    }


_PROFESSION_BY_SIGN = {
    0: "engineering / technical / defense-related fields",
    1: "finance / arts / luxury / land-related work",
    2: "communication / writing / trade / IT",
    3: "care / hospitality / public service / liquids-related",
    4: "leadership / government / administration / performing arts",
    5: "analytics / accounting / healthcare support / service",
    6: "law / diplomacy / design / partnership business",
    7: "research / surgery / occult / investigation / chemistry",
    8: "teaching / law / publishing / advisory / travel",
    9: "management / mining / oil / corporate structure",
    10: "technology / networking / humanitarian / aviation themes",
    11: "medicine / charity / film / spiritual / overseas service",
}

_NATURE_BY_SIGN = {
    0: "energetic, direct, independent",
    1: "steady, sensual, comfort-seeking",
    2: "curious, communicative, adaptable",
    3: "emotional, nurturing, protective",
    4: "confident, expressive, dignified",
    5: "practical, discerning, service-oriented",
    6: "balanced, aesthetic, relationship-focused",
    7: "intense, private, transformative",
    8: "philosophical, expansive, mentoring",
    9: "disciplined, ambitious, reserved",
    10: "unconventional, intellectual, reformist",
    11: "empathetic, imaginative, intuitive",
}


def spouse_prediction(
    lagna: float,
    positions: dict[str, float],
    navamsa: dict,
    karakas: dict,
) -> dict:
    """Spouse profile from 7th house, D9, Venus/DK — traditional sketch only."""
    seventh_sign = (_sign(lagna) + 6) % 12
    seventh_lord = SIGN_LORDS[seventh_sign]
    lord_lon = positions.get(seventh_lord)
    lord_sign = _sign(lord_lon) if lord_lon is not None else seventh_sign
    venus_sign = _sign(positions["Venus"]) if "Venus" in positions else seventh_sign

    d9_7_sign = None
    if "Lagna" in navamsa:
        d9_7_sign = (navamsa["Lagna"]["sign_index"] + 6) % 12
    profile_sign = d9_7_sign if d9_7_sign is not None else lord_sign

    dk = karakas.get("darakaraka", {}).get("planet")
    dk_sign = _sign(positions[dk]) if dk and dk in positions else profile_sign

    # Age difference hint from 7th lord vs Venus speed/dignity (very soft traditional lore)
    age_hint = "similar age range (soft traditional hint)"
    if lord_sign in {9, 10, 11}:  # Capricorn/Aquarius/Pisces flavoured elders in some lore
        age_hint = "spouse may appear more mature / slightly older (traditional hint)"
    if venus_sign in {0, 2, 4}:
        age_hint = "youthful / peer-age tendency (traditional hint)"

    looks = "balanced features; refine via D9 Venus & 7th lord dignity"
    if venus_sign in OWN_SIGNS.get("Venus", []) or EXALTATION.get("Venus") == venus_sign:
        looks = "traditionally associated with refined / attractive presentation"
    height = "average height tendency (weak traditional signal only)"
    if profile_sign in {0, 8}:  # Aries/Sagittarius
        height = "taller-lean tendency (soft signal)"
    if profile_sign in {1, 3}:  # Taurus/Cancer
        height = "medium / well-built tendency (soft signal)"

    finance = "moderate financial capacity; depends on 2nd/11th & dasha"
    if lord_sign in {1, 5, 6, 9} or seventh_lord in {"Venus", "Jupiter"}:
        finance = "generally supportive financial indications (traditional)"

    education = "graduate-level / skilled training tendency"
    if profile_sign in {2, 5, 8, 11}:
        education = "higher education / specialized knowledge tendency"

    native_place = "similar cultural region more often"
    if "Rahu" in positions and _house(positions["Rahu"], lagna) in {7, 9, 12}:
        native_place = "different region / distant or foreign connection tendency"

    return {
        "nature": _NATURE_BY_SIGN[profile_sign],
        "profession_tendency": _PROFESSION_BY_SIGN[profile_sign],
        "education_tendency": education,
        "financial_status": finance,
        "looks": looks,
        "height": height,
        "age_difference": age_hint,
        "native_place_tendency": native_place,
        "anchors": {
            "seventh_sign": SIGNS[seventh_sign],
            "seventh_lord": seventh_lord,
            "seventh_lord_sign": SIGNS[lord_sign],
            "navamsa_seventh_sign": SIGNS[profile_sign],
            "venus_sign": SIGNS[venus_sign],
            "darakaraka": dk,
            "darakaraka_sign": SIGNS[dk_sign],
        },
        "note": (
            "Spouse sketch follows classical house/karaka symbolism. "
            "Treat as cultural interpretation, not a factual forecast."
        ),
    }


def analyze_marriage(chart: dict) -> MarriageAnalysis:
    positions: dict[str, float] = chart["positions"]
    lagna = chart["ascendant"]
    navamsa = _navamsa_map(positions, lagna)
    karakas = _char_karakas(positions)
    ul = _upapada_lagna(lagna, positions)

    seventh_sign = (_sign(lagna) + 6) % 12
    seventh_lord = SIGN_LORDS[seventh_sign]
    seventh = {
        "sign": SIGNS[seventh_sign],
        "lord": seventh_lord,
        "lord_placement": _planet_row(chart, seventh_lord)
        if any(p["name"] == seventh_lord for p in chart["planets"])
        else None,
        "occupants": [
            p["name"]
            for p in chart["planets"]
            if p["house"] == 7 and p["name"] not in {"Uranus", "Neptune", "Pluto"}
        ],
    }

    venus = _planet_row(chart, "Venus")
    jupiter = _planet_row(chart, "Jupiter")

    windows = marriage_timing_windows(
        positions["Moon"],
        chart["utc"],
        lagna,
        positions,
    )
    love = love_marriage_indicators(lagna, positions, navamsa)
    spouse = spouse_prediction(lagna, positions, navamsa, karakas)

    # Strength summary
    strength_pts = 0
    notes = []
    if venus.get("exalted") or venus.get("own_sign"):
        strength_pts += 2
        notes.append("Venus dignified")
    if jupiter.get("exalted") or jupiter.get("own_sign"):
        strength_pts += 2
        notes.append("Jupiter dignified")
    if seventh["lord_placement"] and seventh["lord_placement"]["house"] in {1, 4, 5, 7, 9, 10, 11}:
        strength_pts += 1
        notes.append("7th lord in supportive house")
    if not venus.get("debilitated") and not venus.get("combust"):
        strength_pts += 1

    band = "supportive" if strength_pts >= 4 else "mixed" if strength_pts >= 2 else "challenging"

    return MarriageAnalysis(
        seventh_house=seventh,
        venus=venus,
        jupiter=jupiter,
        navamsa={
            "chart": navamsa,
            "d9_lagna": navamsa.get("Lagna"),
            "d9_seventh": {
                "sign": SIGNS[(navamsa["Lagna"]["sign_index"] + 6) % 12]
                if "Lagna" in navamsa
                else None
            },
        },
        karakas={**karakas, "upapada_lagna": ul},
        timing_windows=windows,
        love_marriage=love,
        spouse_profile=spouse,
        indicators=[],
        summary={
            "relationship_support_band": band,
            "strength_points": strength_pts,
            "notes": notes,
            "top_windows": windows[:3],
        },
    )
