"""Dosha detection (starter set)."""

from __future__ import annotations

from dataclasses import dataclass

from app.jyotish.utils import sign_from_longitude


@dataclass(slots=True)
class DoshaResult:
    key: str
    name: str
    present: bool
    severity: str  # none | low | medium | high
    details: str
    houses_or_planets: list[str]


def _sign(lon: float) -> int:
    return sign_from_longitude(lon).sign_index


def _house(planet_lon: float, lagna_lon: float) -> int:
    return ((_sign(planet_lon) - _sign(lagna_lon)) % 12) + 1


def detect_doshas(
    positions: dict[str, float],
    lagna: float,
) -> list[DoshaResult]:
    results: list[DoshaResult] = []
    mars = positions.get("Mars")
    moon = positions.get("Moon")
    sun = positions.get("Sun")
    rahu = positions.get("Rahu")
    ketu = positions.get("Ketu")
    jupiter = positions.get("Jupiter")
    saturn = positions.get("Saturn")

    # Manglik: Mars in 1,4,7,8,12 (common North-Indian school; variants exist)
    if mars is not None:
        h = _house(mars, lagna)
        present = h in {1, 4, 7, 8, 12}
        results.append(
            DoshaResult(
                key="manglik",
                name="Manglik / Mangal Dosha",
                present=present,
                severity="high" if h in {1, 7, 8} else ("medium" if present else "none"),
                details=f"Mars in house {h} from Lagna (common school).",
                houses_or_planets=[f"Mars-H{h}"],
            )
        )

    # Kaal Sarp: all planets between Rahu and Ketu (simplified hemisphere check)
    if rahu is not None and ketu is not None:
        classic = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        r_sign, k_sign = _sign(rahu), _sign(ketu)
        # Check if all planets lie on one arc Rahu→Ketu
        def between(lon: float) -> bool:
            # arc from Rahu to Ketu going forward
            x = (lon - rahu) % 360
            span = (ketu - rahu) % 360
            return x <= span

        lons = [positions[p] for p in classic if p in positions]
        if lons:
            all_between = all(between(x) for x in lons)
            all_other = all(not between(x) for x in lons)
            present = all_between or all_other
            results.append(
                DoshaResult(
                    key="kaal_sarp",
                    name="Kaal Sarp Dosha",
                    present=present,
                    severity="medium" if present else "none",
                    details="All classic planets on one side of Rahu-Ketu axis (simplified).",
                    houses_or_planets=["Rahu", "Ketu"],
                )
            )

    # Grahan: Sun/Moon with Rahu/Ketu same sign
    for luminary in ("Sun", "Moon"):
        lon = positions.get(luminary)
        if lon is None or rahu is None or ketu is None:
            continue
        present = _sign(lon) in {_sign(rahu), _sign(ketu)}
        results.append(
            DoshaResult(
                key=f"grahan_{luminary.lower()}",
                name=f"Grahan Dosha ({luminary})",
                present=present,
                severity="medium" if present else "none",
                details=f"{luminary} conjunct Rahu/Ketu by sign.",
                houses_or_planets=[luminary, "Rahu/Ketu"],
            )
        )

    # Guru Chandal: Jupiter with Rahu/Ketu
    if jupiter is not None and rahu is not None and ketu is not None:
        present = _sign(jupiter) in {_sign(rahu), _sign(ketu)}
        results.append(
            DoshaResult(
                key="guru_chandal",
                name="Guru Chandal Dosha",
                present=present,
                severity="medium" if present else "none",
                details="Jupiter with Rahu or Ketu (same sign).",
                houses_or_planets=["Jupiter", "Rahu/Ketu"],
            )
        )

    # Kemdrum: no planets in 2nd/12th from Moon (excluding Sun traditionally in some schools)
    if moon is not None:
        m2 = (_sign(moon) + 1) % 12
        m12 = (_sign(moon) + 11) % 12
        others = [
            p
            for p, lon in positions.items()
            if p not in {"Moon", "Uranus", "Neptune", "Pluto"} and _sign(lon) in {m2, m12}
        ]
        present = len(others) == 0
        results.append(
            DoshaResult(
                key="kemdrum",
                name="Kemdrum Dosha",
                present=present,
                severity="medium" if present else "none",
                details="No planets in 2nd/12th from Moon (simplified).",
                houses_or_planets=["Moon"],
            )
        )

    # Shrapit: Saturn + Rahu association
    if saturn is not None and rahu is not None:
        present = _sign(saturn) == _sign(rahu)
        results.append(
            DoshaResult(
                key="shrapit",
                name="Shrapit Dosha",
                present=present,
                severity="medium" if present else "none",
                details="Saturn-Rahu conjunction by sign (simplified).",
                houses_or_planets=["Saturn", "Rahu"],
            )
        )

    # Pitru Dosha hint: Sun afflicted by Rahu/Ketu/Saturn in certain houses
    if sun is not None:
        afflicted = False
        notes = []
        if rahu is not None and _sign(sun) == _sign(rahu):
            afflicted = True
            notes.append("Sun-Rahu")
        if ketu is not None and _sign(sun) == _sign(ketu):
            afflicted = True
            notes.append("Sun-Ketu")
        if saturn is not None and _sign(sun) == _sign(saturn):
            afflicted = True
            notes.append("Sun-Saturn")
        h = _house(sun, lagna)
        if h in {9, 10} and afflicted:
            severity = "high"
        elif afflicted:
            severity = "medium"
        else:
            severity = "none"
        results.append(
            DoshaResult(
                key="pitru",
                name="Pitru Dosha (indicative)",
                present=afflicted,
                severity=severity,
                details="Indicative only; schools differ. " + (", ".join(notes) or "No classic affliction flag."),
                houses_or_planets=notes or ["Sun"],
            )
        )

    return results
