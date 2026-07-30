"""Classical yoga detection (starter set — expandable to 100+)."""

from __future__ import annotations

from dataclasses import dataclass

from app.jyotish.utils import sign_from_longitude


@dataclass(slots=True)
class YogaResult:
    key: str
    name: str
    present: bool
    strength: str  # weak | moderate | strong
    planets_involved: list[str]
    notes: str


def _sign(lon: float) -> int:
    return sign_from_longitude(lon).sign_index


def _house(planet_lon: float, lagna_lon: float) -> int:
    return ((_sign(planet_lon) - _sign(lagna_lon)) % 12) + 1


def detect_yogas(
    positions: dict[str, float],
    lagna: float,
) -> list[YogaResult]:
    """positions: planet name → sidereal longitude."""
    results: list[YogaResult] = []

    sun = positions.get("Sun")
    moon = positions.get("Moon")
    mars = positions.get("Mars")
    mercury = positions.get("Mercury")
    jupiter = positions.get("Jupiter")
    venus = positions.get("Venus")
    saturn = positions.get("Saturn")

    # Gaja Kesari: Jupiter in kendra from Moon
    if moon is not None and jupiter is not None:
        diff = abs(_sign(jupiter) - _sign(moon)) % 12
        present = diff in {0, 3, 6, 9}
        results.append(
            YogaResult(
                key="gaja_kesari",
                name="Gaja Kesari Yoga",
                present=present,
                strength="strong" if present and diff in {0, 6} else ("moderate" if present else "weak"),
                planets_involved=["Moon", "Jupiter"],
                notes="Jupiter in kendra from Moon (classical).",
            )
        )

    # Budha-Aditya: Sun + Mercury same sign
    if sun is not None and mercury is not None:
        present = _sign(sun) == _sign(mercury)
        results.append(
            YogaResult(
                key="budha_aditya",
                name="Budha-Aditya Yoga",
                present=present,
                strength="moderate" if present else "weak",
                planets_involved=["Sun", "Mercury"],
                notes="Sun and Mercury in the same sign.",
            )
        )

    # Chandra Mangal: Moon + Mars same sign
    if moon is not None and mars is not None:
        present = _sign(moon) == _sign(mars)
        results.append(
            YogaResult(
                key="chandra_mangal",
                name="Chandra-Mangal Yoga",
                present=present,
                strength="moderate" if present else "weak",
                planets_involved=["Moon", "Mars"],
                notes="Moon and Mars conjunction (same sign).",
            )
        )

    # Pancha Mahapurusha (simplified: planet in own/exaltation in kendra)
    from app.core.constants import EXALTATION, OWN_SIGNS

    mahapurusha = {
        "Ruchaka": ("Mars", mars),
        "Bhadra": ("Mercury", mercury),
        "Hamsa": ("Jupiter", jupiter),
        "Malavya": ("Venus", venus),
        "Sasa": ("Saturn", saturn),
    }
    for name, (planet, lon) in mahapurusha.items():
        if lon is None:
            continue
        h = _house(lon, lagna)
        s = _sign(lon)
        dignified = s in OWN_SIGNS.get(planet, []) or EXALTATION.get(planet) == s
        present = dignified and h in {1, 4, 7, 10}
        results.append(
            YogaResult(
                key=f"pancha_mahapurusha_{name.lower()}",
                name=f"{name} Yoga (Pancha Mahapurusha)",
                present=present,
                strength="strong" if present else "weak",
                planets_involved=[planet],
                notes=f"{planet} in own/exaltation in kendra.",
            )
        )

    # Amala: benefic in 10th from Moon or Lagna
    if moon is not None and jupiter is not None and venus is not None and mercury is not None:
        tenth_from_lagna = ((_sign(lagna) + 9) % 12)
        tenth_from_moon = ((_sign(moon) + 9) % 12)
        benefics = [("Jupiter", jupiter), ("Venus", venus), ("Mercury", mercury)]
        hit = [p for p, lon in benefics if _sign(lon) in {tenth_from_lagna, tenth_from_moon}]
        results.append(
            YogaResult(
                key="amala",
                name="Amala Yoga",
                present=bool(hit),
                strength="moderate" if hit else "weak",
                planets_involved=hit,
                notes="Benefic in 10th from Lagna or Moon.",
            )
        )

    # Neecha Bhanga (very simplified): debilitated planet with its dispositor in kendra
    from app.core.constants import DEBILITATION, SIGN_LORDS

    for planet, lon in positions.items():
        if planet not in DEBILITATION or lon is None:
            continue
        if _sign(lon) != DEBILITATION[planet]:
            continue
        lord = SIGN_LORDS[_sign(lon)]
        lord_lon = positions.get(lord)
        if lord_lon is None:
            continue
        present = _house(lord_lon, lagna) in {1, 4, 7, 10}
        results.append(
            YogaResult(
                key=f"neecha_bhanga_{planet.lower()}",
                name=f"Neecha Bhanga Raja Yoga ({planet})",
                present=present,
                strength="moderate" if present else "weak",
                planets_involved=[planet, lord],
                notes="Simplified: debilitated planet's dispositor in kendra.",
            )
        )

    # Vipreet Raj (simplified): lords of 6/8/12 in 6/8/12
    dusthana = {6, 8, 12}
    from app.core.constants import SIGN_LORDS as SL

    dusthana_lords: list[str] = []
    for h in dusthana:
        sign = (_sign(lagna) + h - 1) % 12
        dusthana_lords.append(SL[sign])
    for lord in set(dusthana_lords):
        lon = positions.get(lord)
        if lon is None:
            continue
        h = _house(lon, lagna)
        present = h in dusthana
        results.append(
            YogaResult(
                key=f"vipreet_raj_{lord.lower()}",
                name=f"Vipreet Raja Yoga hint ({lord})",
                present=present,
                strength="moderate" if present else "weak",
                planets_involved=[lord],
                notes="Dusthana lord placed in a dusthana (simplified rule).",
            )
        )

    # Lakshmi Yoga hint: Venus strong + Lagna lord strong in kendra/trikona (simplified)
    if venus is not None:
        from app.core.constants import SIGN_LORDS as SL2

        lagna_lord = SL2[_sign(lagna)]
        ll_lon = positions.get(lagna_lord)
        v_ok = _house(venus, lagna) in {1, 4, 5, 7, 9, 10}
        ll_ok = ll_lon is not None and _house(ll_lon, lagna) in {1, 4, 5, 7, 9, 10}
        present = v_ok and ll_ok
        results.append(
            YogaResult(
                key="lakshmi",
                name="Lakshmi Yoga (simplified)",
                present=present,
                strength="moderate" if present else "weak",
                planets_involved=["Venus", lagna_lord],
                notes="Venus and Lagna lord in kendra/trikona (simplified).",
            )
        )

    # Parivartana (mutual exchange)
    planets_classic = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    checked: set[tuple[str, str]] = set()
    for a in planets_classic:
        for b in planets_classic:
            if a >= b:
                continue
            la, lb = positions.get(a), positions.get(b)
            if la is None or lb is None:
                continue
            from app.core.constants import SIGN_LORDS as SL3

            if SL3[_sign(la)] == b and SL3[_sign(lb)] == a:
                key = tuple(sorted((a, b)))
                if key in checked:
                    continue
                checked.add(key)
                results.append(
                    YogaResult(
                        key=f"parivartana_{a.lower()}_{b.lower()}",
                        name=f"Parivartana Yoga ({a}-{b})",
                        present=True,
                        strength="strong",
                        planets_involved=[a, b],
                        notes="Mutual sign exchange.",
                    )
                )

    return results
