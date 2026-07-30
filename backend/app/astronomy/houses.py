"""House cusps and angles."""

from __future__ import annotations

from dataclasses import dataclass

from app.astronomy.ephemeris import init_ephemeris, set_ayanamsha, _try_import_swe


@dataclass(slots=True)
class HouseData:
    system: str
    cusps: list[float]  # 12 sidereal longitudes (houses 1–12)
    ascendant: float
    mc: float
    armc: float
    vertex: float


def calc_houses(
    jd_ut: float,
    latitude: float,
    longitude: float,
    house_system: str = "W",
    ayanamsha: str = "lahiri",
) -> HouseData:
    """Calculate sidereal house cusps."""
    init_ephemeris()
    swe = _try_import_swe()
    if not swe:
        from app.astronomy.approx import approx_houses

        bundle = approx_houses(jd_ut, latitude, longitude, house_system, ayanamsha)
        return HouseData(
            system=bundle.system,
            cusps=bundle.cusps,
            ascendant=bundle.ascendant,
            mc=bundle.mc,
            armc=bundle.armc,
            vertex=bundle.vertex,
        )

    set_ayanamsha(ayanamsha)
    hsys = house_system.encode("ascii")[:1]
    flags = swe.FLG_SIDEREAL | swe.FLG_SWIEPH
    cusps_raw, ascmc = swe.houses_ex(jd_ut, latitude, longitude, hsys, flags)

    cusps = [float(cusps_raw[i]) % 360.0 for i in range(1, 13)]
    asc = float(ascmc[0]) % 360.0
    mc = float(ascmc[1]) % 360.0

    if house_system.upper() == "W":
        lagna_sign = int(asc // 30)
        cusps = [((lagna_sign + i) % 12) * 30.0 for i in range(12)]

    return HouseData(
        system=house_system.upper(),
        cusps=cusps,
        ascendant=asc,
        mc=mc,
        armc=float(ascmc[2]),
        vertex=float(ascmc[3]) % 360.0,
    )


def longitude_to_house(lon: float, cusps: list[float], whole_sign: bool = True) -> int:
    """Return house number 1–12 for a longitude given cusps."""
    lon = lon % 360.0
    if whole_sign:
        lagna_sign = int(cusps[0] // 30)
        planet_sign = int(lon // 30)
        return ((planet_sign - lagna_sign) % 12) + 1

    for i in range(12):
        start = cusps[i]
        end = cusps[(i + 1) % 12]
        if start <= end:
            if start <= lon < end:
                return i + 1
        else:
            if lon >= start or lon < end:
                return i + 1
    return 1
