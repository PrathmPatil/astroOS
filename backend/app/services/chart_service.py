"""Birth chart orchestration across Astronomy + Jyotish layers."""

from __future__ import annotations

from typing import Any

from app.astronomy.ephemeris import birth_to_jd, ephemeris_engine
from app.astronomy.houses import calc_houses, longitude_to_house
from app.astronomy.planets import calc_all_planets, get_ayanamsha_value
from app.core.constants import (
    DISCLAIMER_EN,
    DISCLAIMER_GU,
    DISCLAIMER_HI,
    DISCLAIMER_KN,
    DISCLAIMER_MR,
    DISCLAIMER_TA,
    DISCLAIMER_TE,
    SIGN_LORDS,
)
from app.jyotish.dignity import evaluate_dignity
from app.jyotish.utils import (
    absolute_degree_string,
    nakshatra_from_longitude,
    sign_from_longitude,
)
from app.jyotish.vargas import all_vargas, varga_longitude
from app.schemas import BirthDetails


def disclaimer_for(lang: str = "en") -> str:
    return {
        "en": DISCLAIMER_EN,
        "mr": DISCLAIMER_MR,
        "hi": DISCLAIMER_HI,
        "gu": DISCLAIMER_GU,
        "kn": DISCLAIMER_KN,
        "ta": DISCLAIMER_TA,
        "te": DISCLAIMER_TE,
    }.get(lang, DISCLAIMER_EN)


def compute_chart(birth: BirthDetails) -> dict[str, Any]:
    jd, utc = birth_to_jd(
        birth.year,
        birth.month,
        birth.day,
        birth.hour,
        birth.minute,
        birth.second,
        birth.timezone,
    )
    houses = calc_houses(
        jd,
        birth.latitude,
        birth.longitude,
        birth.house_system,
        birth.ayanamsha,
    )
    planets = calc_all_planets(jd, birth.ayanamsha, include_outer=True)
    ayan = get_ayanamsha_value(jd, birth.ayanamsha)
    sun_lon = planets["Sun"].longitude

    planet_rows = []
    for name, pos in planets.items():
        sp = sign_from_longitude(pos.longitude)
        nak = nakshatra_from_longitude(pos.longitude)
        dig = evaluate_dignity(name, pos.longitude, sun_lon, pos.retrograde)
        house = longitude_to_house(
            pos.longitude,
            houses.cusps,
            whole_sign=birth.house_system.upper() == "W",
        )
        planet_rows.append(
            {
                "name": name,
                "longitude": round(pos.longitude, 6),
                "sign": sp.sign,
                "sign_mr": sp.sign_mr,
                "degree_in_sign": round(sp.degree_in_sign, 4),
                "dms": absolute_degree_string(pos.longitude),
                "nakshatra": nak.name,
                "pada": nak.pada,
                "nakshatra_lord": nak.lord,
                "house": house,
                "retrograde": pos.retrograde,
                "exalted": dig.exalted,
                "debilitated": dig.debilitated,
                "own_sign": dig.own_sign,
                "combust": dig.combust,
                "relationship_to_sign_lord": dig.relationship_to_sign_lord,
            }
        )

    lagna_sp = sign_from_longitude(houses.ascendant)
    lagna_nak = nakshatra_from_longitude(houses.ascendant)
    lagna = {
        "longitude": round(houses.ascendant, 6),
        "sign": lagna_sp.sign,
        "sign_mr": lagna_sp.sign_mr,
        "dms": absolute_degree_string(houses.ascendant),
        "lord": SIGN_LORDS[lagna_sp.sign_index],
        "nakshatra": lagna_nak.name,
        "pada": lagna_nak.pada,
    }

    house_rows = []
    for i, cusp in enumerate(houses.cusps, start=1):
        sp = sign_from_longitude(cusp)
        house_rows.append(
            {
                "number": i,
                "cusp_longitude": round(cusp, 6),
                "sign": sp.sign,
                "sign_lord": SIGN_LORDS[sp.sign_index],
            }
        )

    moon = planets["Moon"]
    moon_sp = sign_from_longitude(moon.longitude)
    moon_nak = nakshatra_from_longitude(moon.longitude)

    positions = {n: p.longitude for n, p in planets.items()}

    return {
        "meta": {
            "name": birth.name,
            "place": birth.place,
            "jd_ut": jd,
            "utc": utc.isoformat(),
            "timezone": birth.timezone,
            "latitude": birth.latitude,
            "longitude": birth.longitude,
            "ayanamsha": birth.ayanamsha,
            "house_system": houses.system,
            "ephemeris_engine": ephemeris_engine(),
        },
        "lagna": lagna,
        "planets": planet_rows,
        "houses": house_rows,
        "moon": {
            "sign": moon_sp.sign,
            "sign_mr": moon_sp.sign_mr,
            "nakshatra": moon_nak.name,
            "pada": moon_nak.pada,
            "lord": moon_nak.lord,
            "longitude": round(moon.longitude, 6),
        },
        "positions": positions,
        "ascendant": houses.ascendant,
        "ayanamsha_value": round(ayan, 6),
        "jd_ut": jd,
        "utc": utc,
        "disclaimer": disclaimer_for("en"),
    }


def compute_vargas(birth: BirthDetails) -> dict[str, Any]:
    chart = compute_chart(birth)
    vargas: dict[str, list[dict[str, Any]]] = {}
    for name, lon in chart["positions"].items():
        divs = all_vargas(lon)
        for varga, vlon in divs.items():
            sp = sign_from_longitude(vlon)
            vargas.setdefault(varga, []).append(
                {
                    "planet": name,
                    "longitude": round(vlon, 6),
                    "sign": sp.sign,
                    "sign_mr": sp.sign_mr,
                    "dms": absolute_degree_string(vlon),
                }
            )
    # Lagna through vargas
    for varga in list(vargas.keys()):
        vlon = varga_longitude(chart["ascendant"], varga)
        sp = sign_from_longitude(vlon)
        vargas[varga].insert(
            0,
            {
                "planet": "Lagna",
                "longitude": round(vlon, 6),
                "sign": sp.sign,
                "sign_mr": sp.sign_mr,
                "dms": absolute_degree_string(vlon),
            },
        )
    return {
        "meta": chart["meta"],
        "vargas": vargas,
        "disclaimer": disclaimer_for("en"),
    }
