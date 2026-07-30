"""Audit Engine — Prediction → Evidence → Rule → Planet → House → Book → Sloka."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

_PLANET_RE = re.compile(
    r"\b(Sun|Moon|Mars|Mercury|Jupiter|Venus|Saturn|Rahu|Ketu)\b", re.I
)
_HOUSE_RE = re.compile(r"\bH(?:ouse)?\s*(\d{1,2})\b|\bin house (\d{1,2})\b", re.I)


def _extract_planets_houses(evidence: list[str], rule_details: list[dict]) -> tuple[list[str], list[int]]:
    planets: list[str] = []
    houses: list[int] = []
    blobs = list(evidence) + [
        " ".join(r.get("evidence_checks") or []) for r in rule_details
    ]
    for blob in blobs:
        for m in _PLANET_RE.findall(blob):
            p = m.title() if m.lower() != "sun" else "Sun"
            # normalize
            p = m[0].upper() + m[1:].lower()
            if p == "Sun" or p in {
                "Moon",
                "Mars",
                "Mercury",
                "Jupiter",
                "Venus",
                "Saturn",
                "Rahu",
                "Ketu",
            }:
                planets.append(p if p != "sun" else "Sun")
        for m in _HOUSE_RE.finditer(blob):
            num = m.group(1) or m.group(2)
            if num:
                houses.append(int(num))
    # unique preserve
    up, uh = [], []
    for p in planets:
        key = p.capitalize() if p.lower() not in {"rahu", "ketu"} else p.capitalize()
        # fix Rahu/Ketu
        if p.lower() == "rahu":
            key = "Rahu"
        elif p.lower() == "ketu":
            key = "Ketu"
        elif p.lower() == "sun":
            key = "Sun"
        else:
            key = p[0].upper() + p[1:].lower()
        if key not in up:
            up.append(key)
    for h in houses:
        if h not in uh and 1 <= h <= 12:
            uh.append(h)
    return up, uh


def build_audit_trail(
    conclusion: dict[str, Any],
    chart_meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    evidence = conclusion.get("evidence", [])
    rule_details = conclusion.get("rule_details", [])
    planets, houses = _extract_planets_houses(evidence, rule_details)

    chain: list[dict[str, Any]] = [
        {"step": "prediction", "value": conclusion.get("title"), "key": conclusion.get("conclusion_key")},
        {"step": "evidence", "items": evidence},
        {"step": "rules", "items": conclusion.get("used_rules", [])},
        {"step": "planets", "items": planets},
        {"step": "houses", "items": houses},
    ]
    for src in conclusion.get("sources", []):
        chain.append(
            {
                "step": "book_sloka",
                "rule_id": src.get("rule_id"),
                "book": src.get("text"),
                "sloka_id": src.get("sloka_id"),
                "chapter": src.get("chapter"),
                "sloka_ref": src.get("sloka"),
                "sanskrit": src.get("sanskrit"),
                "translations": {
                    "en": src.get("english"),
                    "mr": src.get("marathi"),
                    "hi": src.get("hindi"),
                    "gu": src.get("gujarati"),
                    "kn": src.get("kannada"),
                    "ta": src.get("tamil"),
                    "te": src.get("telugu"),
                },
            }
        )

    return {
        "audit_id": str(uuid4()),
        "created_at": datetime.now(tz=timezone.utc).isoformat(),
        "chart_meta": chart_meta or {},
        "prediction": {
            "conclusion_key": conclusion.get("conclusion_key"),
            "title": conclusion.get("title"),
            "summary": conclusion.get("summary"),
            "confidence": conclusion.get("confidence"),
        },
        "evidence": evidence,
        "rules": conclusion.get("used_rules", []),
        "planets": planets,
        "houses": houses,
        "rule_details": rule_details,
        "classical_chain": [c for c in chain if c["step"] == "book_sloka"],
        "full_chain": chain,
        "verifiability": {
            "transparent": True,
            "ai_invented": False,
            "chain": "prediction→evidence→rule→planet→house→book→sloka",
            "note": "Every step is rule/evidence backed; AI may only rephrase this chain.",
        },
    }
