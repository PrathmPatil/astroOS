"""Transit engine — daily / weekly / monthly / yearly for Sa/Ju/Ra/Ke."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from app.astronomy.ephemeris import datetime_to_jd_ut, init_ephemeris
from app.astronomy.planets import calc_planet
from app.jyotish.utils import sign_from_longitude
from app.schemas import BirthDetails
from app.services.chart_service import compute_chart, disclaimer_for


KEY_PLANETS = ["Saturn", "Jupiter", "Rahu", "Ketu", "Sun", "Moon", "Mars", "Venus", "Mercury"]


def _house(transit_lon: float, lagna: float) -> int:
    return ((int(sign_from_longitude(transit_lon).sign_index) - int(sign_from_longitude(lagna).sign_index)) % 12) + 1


def _snapshot(jd: float, ayanamsha: str, lagna: float) -> list[dict[str, Any]]:
    rows = []
    for name in KEY_PLANETS:
        pos = calc_planet(jd, name, ayanamsha)
        sp = sign_from_longitude(pos.longitude)
        rows.append(
            {
                "planet": name,
                "longitude": round(pos.longitude, 4),
                "sign": sp.sign,
                "house_from_natal_lagna": _house(pos.longitude, lagna),
                "retrograde": pos.retrograde,
            }
        )
    return rows


def transit_periods(birth: BirthDetails, at: datetime | None = None) -> dict[str, Any]:
    chart = compute_chart(birth)
    lagna = chart["ascendant"]
    init_ephemeris()
    when = at or datetime.now(tz=ZoneInfo("UTC"))
    if when.tzinfo is None:
        when = when.replace(tzinfo=ZoneInfo("UTC"))
    when = when.astimezone(ZoneInfo("UTC"))

    def jd_for(dt: datetime) -> float:
        return datetime_to_jd_ut(dt.astimezone(ZoneInfo("UTC")))

    daily = _snapshot(jd_for(when), birth.ayanamsha, lagna)
    weekly = _snapshot(jd_for(when + timedelta(days=7)), birth.ayanamsha, lagna)
    monthly = _snapshot(jd_for(when + timedelta(days=30)), birth.ayanamsha, lagna)
    yearly = _snapshot(jd_for(when + timedelta(days=365)), birth.ayanamsha, lagna)

    # Focus Sa/Ju/Ra/Ke narratives
    focus = {}
    for name in ["Saturn", "Jupiter", "Rahu", "Ketu"]:
        now = next(p for p in daily if p["planet"] == name)
        later_y = next(p for p in yearly if p["planet"] == name)
        focus[name] = {
            "now": now,
            "in_one_year": later_y,
            "sign_change_likely": now["sign"] != later_y["sign"],
            "houses_watched": [1, 4, 7, 10, 5, 9],
            "active_on_natal_kendra": now["house_from_natal_lagna"] in {1, 4, 7, 10},
        }

    return {
        "at": when.isoformat(),
        "natal_lagna": chart["lagna"],
        "periods": {
            "daily": daily,
            "weekly": weekly,
            "monthly": monthly,
            "yearly": yearly,
        },
        "slow_planets": focus,
        "disclaimer": disclaimer_for("en"),
    }
