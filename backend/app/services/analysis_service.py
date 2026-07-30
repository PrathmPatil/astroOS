from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from app.jyotish.dasha import current_dasha
from app.jyotish.doshas import detect_doshas
from app.jyotish.yogas import detect_yogas
from app.schemas import BirthDetails, GunMilanRequest
from app.services.chart_service import compute_chart, disclaimer_for


def compute_dasha(birth: BirthDetails, at: datetime | None = None) -> dict:
    chart = compute_chart(birth)
    data = current_dasha(chart["positions"]["Moon"], chart["utc"], at)

    def ser(p):
        return {
            "lord": p.lord,
            "start": p.start,
            "end": p.end,
            "level": p.level,
            "parent": p.parent,
        }

    return {
        "current_mahadasha": ser(data["mahadasha"]),
        "current_antardasha": ser(data["antardasha"]),
        "mahadashas": [ser(p) for p in data["mahadashas"]],
        "antardashas": [ser(p) for p in data["antardashas"]],
        "disclaimer": disclaimer_for("en"),
    }


def compute_yogas(birth: BirthDetails) -> dict:
    chart = compute_chart(birth)
    yogas = detect_yogas(chart["positions"], chart["ascendant"])
    return {
        "yogas": [
            {
                "key": y.key,
                "name": y.name,
                "present": y.present,
                "strength": y.strength,
                "planets_involved": y.planets_involved,
                "notes": y.notes,
            }
            for y in yogas
        ],
        "present_count": sum(1 for y in yogas if y.present),
        "disclaimer": disclaimer_for("en"),
    }


def compute_doshas(birth: BirthDetails) -> dict:
    chart = compute_chart(birth)
    doshas = detect_doshas(chart["positions"], chart["ascendant"])
    return {
        "doshas": [
            {
                "key": d.key,
                "name": d.name,
                "present": d.present,
                "severity": d.severity,
                "details": d.details,
                "houses_or_planets": d.houses_or_planets,
            }
            for d in doshas
        ],
        "present_count": sum(1 for d in doshas if d.present),
        "disclaimer": disclaimer_for("en"),
    }


def compute_gun_milan(payload: GunMilanRequest) -> dict:
    from app.services.matchmaking_service import compute_gun_milan_enriched

    return compute_gun_milan_enriched(payload)


def compute_transit(birth: BirthDetails, at: datetime | None = None) -> dict:
    """Compare natal positions with current sky (sidereal)."""
    from app.astronomy.ephemeris import datetime_to_jd_ut, init_ephemeris
    from app.astronomy.planets import calc_all_planets
    from app.jyotish.utils import sign_from_longitude

    chart = compute_chart(birth)
    init_ephemeris()
    when = at or datetime.now(tz=ZoneInfo("UTC"))
    if when.tzinfo is None:
        when = when.replace(tzinfo=ZoneInfo("UTC"))
    jd = datetime_to_jd_ut(when.astimezone(ZoneInfo("UTC")))
    transit = calc_all_planets(jd, birth.ayanamsha, include_outer=True)

    rows = []
    for name, pos in transit.items():
        natal = chart["positions"].get(name)
        sp = sign_from_longitude(pos.longitude)
        rows.append(
            {
                "planet": name,
                "transit_longitude": round(pos.longitude, 6),
                "transit_sign": sp.sign,
                "natal_longitude": round(natal, 6) if natal is not None else None,
                "retrograde": pos.retrograde,
            }
        )
    return {
        "at": when.isoformat(),
        "transits": rows,
        "natal_lagna": chart["lagna"],
        "disclaimer": disclaimer_for("en"),
    }


def marriage_overview(birth: BirthDetails) -> dict:
    """Backward-compatible alias — prefer app.services.marriage_service."""
    from app.services.marriage_service import marriage_full_report

    return marriage_full_report(birth)
