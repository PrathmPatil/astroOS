"""Swiss Ephemeris bootstrap and Julian Day helpers."""

from __future__ import annotations

from datetime import datetime
from functools import lru_cache
from pathlib import Path
from zoneinfo import ZoneInfo

from app.core.config import get_settings

_SWE = None


def _try_import_swe():
    global _SWE
    if _SWE is not None:
        return _SWE
    try:
        import swisseph as swe

        _SWE = swe
    except Exception:
        _SWE = False
    return _SWE


AYANAMSHA_NAMES = ("lahiri", "raman", "krishnamurti")


@lru_cache
def init_ephemeris(ephe_path: str | None = None) -> str:
    """Initialize Swiss Ephemeris path once per process (no-op if unavailable)."""
    settings = get_settings()
    path = ephe_path or settings.se_ephe_path
    resolved = str(Path(path).resolve())
    Path(resolved).mkdir(parents=True, exist_ok=True)
    swe = _try_import_swe()
    if swe:
        swe.set_ephe_path(resolved)
    return resolved


def ephemeris_engine() -> str:
    swe = _try_import_swe()
    return "swiss_ephemeris" if swe else "approximate_dev"


def set_ayanamsha(name: str = "lahiri") -> None:
    swe = _try_import_swe()
    if not swe:
        return
    mapping = {
        "lahiri": swe.SIDM_LAHIRI,
        "raman": swe.SIDM_RAMAN,
        "krishnamurti": swe.SIDM_KRISHNAMURTI,
    }
    swe.set_sid_mode(mapping.get(name.lower(), swe.SIDM_LAHIRI))


def local_to_utc(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    second: float,
    timezone: str,
) -> datetime:
    """Convert local civil time to aware UTC datetime."""
    local = datetime(
        year,
        month,
        day,
        hour,
        minute,
        int(second),
        int((second % 1) * 1_000_000),
        tzinfo=ZoneInfo(timezone),
    )
    return local.astimezone(ZoneInfo("UTC"))


def datetime_to_jd_ut(dt_utc: datetime) -> float:
    """Convert UTC datetime to Julian Day (UT)."""
    if dt_utc.tzinfo is None:
        raise ValueError("datetime must be timezone-aware (UTC)")
    utc = dt_utc.astimezone(ZoneInfo("UTC"))
    second = utc.second + utc.microsecond / 1_000_000.0
    swe = _try_import_swe()
    if swe:
        _jd_et, jd_ut = swe.utc_to_jd(
            utc.year,
            utc.month,
            utc.day,
            utc.hour,
            utc.minute,
            second,
            swe.GREG_CAL,
        )
        return float(jd_ut)

    # Meeus-style fallback JD
    y, m = utc.year, utc.month
    d = utc.day + (utc.hour + utc.minute / 60.0 + second / 3600.0) / 24.0
    if m <= 2:
        y -= 1
        m += 12
    a = y // 100
    b = 2 - a + a // 4
    return int(365.25 * (y + 4716)) + int(30.6001 * (m + 1)) + d + b - 1524.5


def birth_to_jd(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    second: float,
    timezone: str,
) -> tuple[float, datetime]:
    """Return (jd_ut, utc_datetime) for birth data."""
    init_ephemeris()
    utc = local_to_utc(year, month, day, hour, minute, second, timezone)
    return datetime_to_jd_ut(utc), utc
