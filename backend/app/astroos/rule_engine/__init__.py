"""AstroOS Rule Engine — match YAML classical rules against a chart context."""

from __future__ import annotations

from typing import Any

from app.astroos.knowledge import get_sloka, rules_by_category
from app.core.constants import EXALTATION, OWN_SIGNS, SIGN_LORDS
from app.jyotish.utils import sign_from_longitude


def _sign(lon: float) -> int:
    return sign_from_longitude(lon).sign_index


def _house(planet_lon: float, lagna: float) -> int:
    return ((_sign(planet_lon) - _sign(lagna)) % 12) + 1


def build_context(chart: dict, extras: dict | None = None) -> dict[str, Any]:
    """Normalize chart dict into evaluable context."""
    positions = chart["positions"]
    lagna = chart["ascendant"]
    planets = {p["name"]: p for p in chart["planets"]}
    ctx: dict[str, Any] = {
        "positions": positions,
        "lagna": lagna,
        "planets": planets,
        "houses": {
            name: _house(lon, lagna)
            for name, lon in positions.items()
            if name not in {"Uranus", "Neptune", "Pluto"}
        },
        "signs": {name: _sign(lon) for name, lon in positions.items()},
    }
    if extras:
        ctx.update(extras)
    return ctx


def _eval_item(item: dict[str, Any], ctx: dict[str, Any]) -> tuple[bool, str]:
    if "planet_in_kendra" in item:
        planet = item["planet_in_kendra"]
        h = ctx["houses"].get(planet)
        ok = h in {1, 4, 7, 10}
        return ok, f"{planet} in house {h} (kendra={ok})"

    if "same_sign" in item:
        a, b = item["same_sign"]
        ok = ctx["signs"].get(a) == ctx["signs"].get(b)
        return ok, f"{a}/{b} same sign={ok}"

    if "planet_in_houses" in item:
        spec = item["planet_in_houses"]
        planet = spec["planet"]
        houses = set(spec["houses"])
        h = ctx["houses"].get(planet)
        ok = h in houses
        return ok, f"{planet} in H{h} (need {sorted(houses)}) → {ok}"

    if "planet_dignity" in item:
        spec = item["planet_dignity"]
        planet = spec["planet"]
        status = spec["status"]
        row = ctx["planets"].get(planet, {})
        if status == "debilitated":
            ok = bool(row.get("debilitated"))
        elif status == "exalted":
            ok = bool(row.get("exalted"))
        elif status == "own_sign":
            ok = bool(row.get("own_sign"))
        else:
            ok = False
        return ok, f"{planet} dignity {status}={ok}"

    if "kemdrum" in item:
        moon_h_sign = ctx["signs"].get("Moon")
        if moon_h_sign is None:
            return False, "Moon missing"
        m2 = (moon_h_sign + 1) % 12
        m12 = (moon_h_sign + 11) % 12
        others = [
            p
            for p, s in ctx["signs"].items()
            if p not in {"Moon", "Uranus", "Neptune", "Pluto"} and s in {m2, m12}
        ]
        ok = len(others) == 0
        return ok, f"Kemdrum pattern={ok}"

    if "house_lord_strong" in item:
        house = int(item["house_lord_strong"])
        lord = SIGN_LORDS[(_sign(ctx["lagna"]) + house - 1) % 12]
        h = ctx["houses"].get(lord)
        row = ctx["planets"].get(lord, {})
        ok = (h in {1, 4, 5, 7, 9, 10, 11}) or row.get("exalted") or row.get("own_sign")
        return ok, f"{house}th lord {lord} in H{h} strong={ok}"

    if "navamsa_focus" in item:
        # Always true when we run marriage/navamsa analysis path — flagged by extras
        ok = bool(ctx.get("navamsa_examined", True))
        return ok, f"Navamsa focus examined={ok}"

    if "current_dasha_involves_7th_lord" in item:
        seventh_lord = SIGN_LORDS[(_sign(ctx["lagna"]) + 6) % 12]
        md = ctx.get("mahadasha")
        ad = ctx.get("antardasha")
        ok = seventh_lord in {md, ad} or "Venus" in {md, ad} or "Jupiter" in {md, ad}
        return ok, f"Dasha {md}/{ad} vs 7th lord {seventh_lord} → {ok}"

    if "transit_planet_aspects_natal_house" in item:
        spec = item["transit_planet_aspects_natal_house"]
        planet = spec["planet"]
        houses = set(spec["houses"])
        transit_houses = ctx.get("transit_houses", {})
        h = transit_houses.get(planet)
        ok = h in houses if h is not None else False
        return ok, f"Transit {planet} on natal H{h} (need {sorted(houses)}) → {ok}"

    return False, f"Unknown condition {item}"


def _eval_conditions(conds: dict[str, Any], ctx: dict[str, Any]) -> tuple[bool, list[str]]:
    items = conds.get("items", [])
    mode = conds.get("type", "all")
    evidence_lines: list[str] = []
    results: list[bool] = []
    for item in items:
        ok, line = _eval_item(item, ctx)
        results.append(ok)
        evidence_lines.append(("✓ " if ok else "✗ ") + line)
    if mode == "any":
        return any(results), evidence_lines
    return all(results) if results else False, evidence_lines


def match_rules(
    chart: dict,
    category: str | None = None,
    extras: dict | None = None,
) -> list[dict[str, Any]]:
    ctx = build_context(chart, extras)
    matched: list[dict[str, Any]] = []
    for rule in rules_by_category(category):
        ok, lines = _eval_conditions(rule.get("conditions", {}), ctx)
        if not ok:
            continue
        sloka = get_sloka((rule.get("source") or {}).get("sloka_id"))
        matched.append(
            {
                "rule_id": rule["rule_id"],
                "name": rule["name"],
                "category": rule.get("category"),
                "priority": rule.get("priority", 50),
                "weight": rule.get("weight", 0.5),
                "confidence_base": rule.get("confidence_base", 0.5),
                "result": rule.get("result", {}),
                "source": rule.get("source", {}),
                "modern_interpretation": rule.get("modern_interpretation"),
                "conflicts": rule.get("conflicts", []),
                "evidence_checks": lines,
                "sloka": sloka,
                "file": rule.get("_file"),
            }
        )
    matched.sort(key=lambda r: (-r["priority"], r["rule_id"]))
    return matched
