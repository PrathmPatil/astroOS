"""House systems including Whole, Equal, Placidus, KP (Placidus-based), Sripati."""

from __future__ import annotations

from dataclasses import dataclass

from app.astronomy.ephemeris import init_ephemeris, set_ayanamsha, _try_import_swe
from app.astronomy.houses import HouseData


HOUSE_SYSTEMS = {
    "W": "Whole Sign",
    "E": "Equal",
    "P": "Placidus",
    "KP": "KP (Placidus cusps — Krishnamurti standard)",
    "S": "Sripati (Porphyry quadrant trisection)",
}


def _sripati_cusps(asc: float, mc: float) -> list[float]:
    """Sripati/Porphyry: trisect each quadrant between angles."""

    def norm(x: float) -> float:
        return x % 360.0

    desc = norm(asc + 180.0)
    ic = norm(mc + 180.0)
    # Quadrants: Asc→IC→Desc→MC→Asc (depending on hemisphere); use Asc, IC, Desc, MC order
    angles = [asc, ic, desc, mc]
    # Ensure forward arcs
    cusps = [0.0] * 12
    # House 1 = Asc, 4 = IC, 7 = Desc, 10 = MC
    cusps[0] = norm(asc)
    cusps[3] = norm(ic)
    cusps[6] = norm(desc)
    cusps[9] = norm(mc)

    def trisect(start: float, end: float) -> tuple[float, float]:
        arc = (end - start) % 360.0
        return norm(start + arc / 3.0), norm(start + 2.0 * arc / 3.0)

    # Asc → IC : houses 2, 3
    c2, c3 = trisect(asc, ic)
    cusps[1], cusps[2] = c2, c3
    # IC → Desc : houses 5, 6
    c5, c6 = trisect(ic, desc)
    cusps[4], cusps[5] = c5, c6
    # Desc → MC : houses 8, 9
    c8, c9 = trisect(desc, mc)
    cusps[7], cusps[8] = c8, c9
    # MC → Asc : houses 11, 12
    c11, c12 = trisect(mc, asc)
    cusps[10], cusps[11] = c11, c12
    return cusps


def calc_houses_advanced(
    jd_ut: float,
    latitude: float,
    longitude: float,
    house_system: str = "W",
    ayanamsha: str = "lahiri",
) -> HouseData:
    init_ephemeris()
    code = house_system.upper()
    swe = _try_import_swe()

    # Map KP → Placidus engine code
    swe_code = {"W": "W", "E": "E", "P": "P", "KP": "P", "S": "O", "O": "O", "K": "K"}.get(
        code, "W"
    )

    if not swe:
        from app.astronomy.approx import approx_houses

        bundle = approx_houses(jd_ut, latitude, longitude, "W" if code == "W" else "E", ayanamsha)
        cusps = bundle.cusps
        if code == "S":
            cusps = _sripati_cusps(bundle.ascendant, bundle.mc)
        return HouseData(
            system=code,
            cusps=cusps,
            ascendant=bundle.ascendant,
            mc=bundle.mc,
            armc=bundle.armc,
            vertex=bundle.vertex,
        )

    set_ayanamsha(ayanamsha)
    flags = swe.FLG_SIDEREAL | swe.FLG_SWIEPH
    hsys = swe_code.encode("ascii")[:1]
    cusps_raw, ascmc = swe.houses_ex(jd_ut, latitude, longitude, hsys, flags)
    cusps = [float(cusps_raw[i]) % 360.0 for i in range(1, 13)]
    asc = float(ascmc[0]) % 360.0
    mc = float(ascmc[1]) % 360.0

    if code == "W":
        lagna_sign = int(asc // 30)
        cusps = [((lagna_sign + i) % 12) * 30.0 for i in range(12)]
    elif code == "S":
        cusps = _sripati_cusps(asc, mc)

    return HouseData(
        system=code,
        cusps=cusps,
        ascendant=asc,
        mc=mc,
        armc=float(ascmc[2]),
        vertex=float(ascmc[3]) % 360.0,
    )
