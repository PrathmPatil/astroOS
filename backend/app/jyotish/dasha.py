"""Vimshottari dasha engine (maha / antar)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.core.constants import VIMSHOTTARI_ORDER, VIMSHOTTARI_YEARS
from app.jyotish.utils import NAKSHATRA_SPAN, nakshatra_from_longitude

DAYS_PER_YEAR = 365.2425


@dataclass(slots=True)
class DashaPeriod:
    lord: str
    start: datetime
    end: datetime
    level: str  # maha | antar
    parent: str | None = None


def _add_years(dt: datetime, years: float) -> datetime:
    return dt + timedelta(days=years * DAYS_PER_YEAR)


def moon_balance_at_birth(moon_longitude: float) -> tuple[str, float]:
    """Return (dasha_lord, remaining_fraction of mahadasha)."""
    nak = nakshatra_from_longitude(moon_longitude)
    lord = nak.lord
    elapsed = (moon_longitude % 360.0) % NAKSHATRA_SPAN
    remaining_frac = 1.0 - (elapsed / NAKSHATRA_SPAN)
    return lord, remaining_frac


def vimshottari_mahadashas(
    moon_longitude: float,
    birth_utc: datetime,
    cycles: int = 1,
) -> list[DashaPeriod]:
    lord, remaining_frac = moon_balance_at_birth(moon_longitude)
    start_idx = VIMSHOTTARI_ORDER.index(lord)
    periods: list[DashaPeriod] = []
    cursor = birth_utc

    # Balance of first dasha
    first_years = VIMSHOTTARI_YEARS[lord] * remaining_frac
    end = _add_years(cursor, first_years)
    periods.append(DashaPeriod(lord=lord, start=cursor, end=end, level="maha"))
    cursor = end

    order = VIMSHOTTARI_ORDER
    total = len(order) * cycles
    idx = start_idx + 1
    for _ in range(total - 1):
        lord_name = order[idx % len(order)]
        years = VIMSHOTTARI_YEARS[lord_name]
        end = _add_years(cursor, years)
        periods.append(
            DashaPeriod(lord=lord_name, start=cursor, end=end, level="maha")
        )
        cursor = end
        idx += 1
    return periods


def antar_dashas(maha: DashaPeriod) -> list[DashaPeriod]:
    """Compute antardashas within a mahadasha."""
    maha_years = (maha.end - maha.start).total_seconds() / (DAYS_PER_YEAR * 86400)
    start_idx = VIMSHOTTARI_ORDER.index(maha.lord)
    periods: list[DashaPeriod] = []
    cursor = maha.start
    for i in range(9):
        lord = VIMSHOTTARI_ORDER[(start_idx + i) % 9]
        portion = (VIMSHOTTARI_YEARS[lord] / 120.0) * maha_years
        end = _add_years(cursor, portion)
        if end > maha.end:
            end = maha.end
        periods.append(
            DashaPeriod(
                lord=lord,
                start=cursor,
                end=end,
                level="antar",
                parent=maha.lord,
            )
        )
        cursor = end
        if cursor >= maha.end:
            break
    return periods


def current_dasha(
    moon_longitude: float,
    birth_utc: datetime,
    at: datetime | None = None,
) -> dict:
    at = at or datetime.now(tz=ZoneInfo("UTC"))
    if at.tzinfo is None:
        at = at.replace(tzinfo=ZoneInfo("UTC"))
    mahas = vimshottari_mahadashas(moon_longitude, birth_utc, cycles=2)
    current_maha = next((p for p in mahas if p.start <= at < p.end), mahas[-1])
    antars = antar_dashas(current_maha)
    current_antar = next((p for p in antars if p.start <= at < p.end), antars[-1])
    return {
        "mahadasha": current_maha,
        "antardasha": current_antar,
        "mahadashas": mahas,
        "antardashas": antars,
    }
