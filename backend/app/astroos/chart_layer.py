"""Astronomy + Chart layer with full Shadbala and advanced house systems."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from app.astronomy.ephemeris import birth_to_jd
from app.astronomy.house_systems import HOUSE_SYSTEMS, calc_houses_advanced
from app.astronomy.planets import calc_all_planets, get_ayanamsha_value
from app.jyotish.dignity import evaluate_dignity
from app.jyotish.shadbala import compute_shadbala
from app.jyotish.utils import absolute_degree_string, nakshatra_from_longitude, sign_from_longitude
from app.schemas import BirthDetails

AYANAMSHA_OPTIONS = ["lahiri", "raman", "krishnamurti"]
EPHEMERIS_MODES = ["swiss", "jpl_if_available", "approximate_dev"]


def astronomy_snapshot(birth: BirthDetails) -> dict[str, Any]:
    jd, utc = birth_to_jd(
        birth.year,
        birth.month,
        birth.day,
        birth.hour,
        birth.minute,
        birth.second,
        birth.timezone,
    )
    planets = calc_all_planets(jd, birth.ayanamsha, include_outer=True)
    houses = calc_houses_advanced(
        jd, birth.latitude, birth.longitude, birth.house_system, birth.ayanamsha
    )
    sun = planets["Sun"].longitude
    lagna_sign = int(houses.ascendant // 30)

    house_map: dict[str, int] = {}
    positions = {n: p.longitude for n, p in planets.items()}
    for name, pos in planets.items():
        sp = sign_from_longitude(pos.longitude)
        if birth.house_system.upper() == "W":
            house_map[name] = ((sp.sign_index - lagna_sign) % 12) + 1
        else:
            # cusp-based for quadrant systems
            from app.astronomy.houses import longitude_to_house

            house_map[name] = longitude_to_house(pos.longitude, houses.cusps, whole_sign=False)

    # Day birth approx: local hour between sunrise proxy 6-18
    local = datetime(
        birth.year, birth.month, birth.day, birth.hour, birth.minute, tzinfo=ZoneInfo(birth.timezone)
    )
    is_day = 6 <= local.hour < 18
    weekday = local.weekday()

    rows = []
    for name, pos in planets.items():
        if name in {"Uranus", "Neptune", "Pluto"}:
            continue
        dig = evaluate_dignity(name, pos.longitude, sun, pos.retrograde)
        sp = sign_from_longitude(pos.longitude)
        nak = nakshatra_from_longitude(pos.longitude)
        house = house_map[name]
        row = {
            "name": name,
            "longitude": round(pos.longitude, 6),
            "latitude": round(pos.latitude, 6),
            "speed": round(pos.speed_longitude, 6),
            "retrograde": pos.retrograde,
            "sign": sp.sign,
            "dms": absolute_degree_string(pos.longitude),
            "nakshatra": nak.name,
            "pada": nak.pada,
            "exalted": dig.exalted,
            "debilitated": dig.debilitated,
            "own_sign": dig.own_sign,
            "friend_enemy": dig.relationship_to_sign_lord,
            "combust": dig.combust,
            "house": house,
        }
        row["shadbala"] = compute_shadbala(
            name,
            pos.longitude,
            house,
            pos.speed_longitude,
            pos.retrograde,
            positions,
            house_map,
            is_day,
            weekday,
        )
        rows.append(row)

    return {
        "jd_ut": jd,
        "utc": utc.isoformat(),
        "ayanamsha": birth.ayanamsha,
        "ayanamsha_value": get_ayanamsha_value(jd, birth.ayanamsha),
        "ayanamsha_options": AYANAMSHA_OPTIONS,
        "ephemeris_modes": EPHEMERIS_MODES,
        "house_system": houses.system,
        "house_systems_available": HOUSE_SYSTEMS,
        "ascendant": houses.ascendant,
        "mc": houses.mc,
        "planets": rows,
    }


def chart_engine_bundle(birth: BirthDetails) -> dict[str, Any]:
    from app.services.chart_service import compute_chart, compute_vargas

    chart = compute_chart(birth)
    vargas = compute_vargas(birth)
    jd, _ = birth_to_jd(
        birth.year,
        birth.month,
        birth.day,
        birth.hour,
        birth.minute,
        birth.second,
        birth.timezone,
    )
    systems = {}
    for code, name in HOUSE_SYSTEMS.items():
        try:
            h = calc_houses_advanced(jd, birth.latitude, birth.longitude, code, birth.ayanamsha)
            systems[code] = {
                "name": name,
                "ascendant": round(h.ascendant, 4),
                "mc": round(h.mc, 4),
                "cusps": [round(x, 4) for x in h.cusps],
            }
        except Exception as exc:  # noqa: BLE001
            systems[code] = {"name": name, "error": str(exc)}

    return {
        "d1": chart,
        "vargas": vargas["vargas"],
        "house_systems": systems,
        "divisional_list": list(vargas["vargas"].keys()),
        "astronomy": astronomy_snapshot(birth),
    }
