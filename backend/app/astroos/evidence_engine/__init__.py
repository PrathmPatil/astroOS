"""Evidence Engine — USP: every conclusion carries evidence, rules, sources, confidence."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from app.astroos.rule_engine import match_rules
from app.core.constants import (
    DISCLAIMER_EN,
    DISCLAIMER_GU,
    DISCLAIMER_HI,
    DISCLAIMER_KN,
    DISCLAIMER_MR,
    DISCLAIMER_TA,
    DISCLAIMER_TE,
)


def _confidence(rules: list[dict[str, Any]]) -> float:
    if not rules:
        return 0.0
    # Weighted average of confidence_base * weight, boosted by rule count (cap 0.95)
    num = sum(r["confidence_base"] * r["weight"] for r in rules)
    den = sum(r["weight"] for r in rules) or 1.0
    base = num / den
    boost = min(0.12, 0.03 * (len(rules) - 1))
    return round(min(0.95, base + boost) * 100, 1)


def group_conclusions(matched: list[dict[str, Any]]) -> list[dict[str, Any]]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for rule in matched:
        key = (rule.get("result") or {}).get("conclusion_key") or rule["rule_id"]
        buckets[key].append(rule)

    conclusions: list[dict[str, Any]] = []
    for key, rules in buckets.items():
        evidence_lines: list[str] = []
        for r in rules:
            evidence_lines.extend(r.get("evidence_checks", []))
        # unique preserve order
        seen = set()
        uniq_ev = []
        for line in evidence_lines:
            if line.startswith("✓") and line not in seen:
                seen.add(line)
                uniq_ev.append(line)

        sources = []
        for r in rules:
            sloka = r.get("sloka")
            src = r.get("source") or {}
            sources.append(
                {
                    "rule_id": r["rule_id"],
                    "text": src.get("text"),
                    "sloka_id": src.get("sloka_id"),
                    "chapter": sloka.get("chapter") if sloka else None,
                    "sloka": sloka.get("sloka") if sloka else None,
                    "sanskrit": sloka.get("sanskrit") if sloka else None,
                    "english": sloka.get("english") if sloka else None,
                    "marathi": sloka.get("marathi") if sloka else None,
                    "hindi": sloka.get("hindi") if sloka else None,
                    "gujarati": sloka.get("gujarati") if sloka else None,
                    "kannada": sloka.get("kannada") if sloka else None,
                    "tamil": sloka.get("tamil") if sloka else None,
                    "telugu": sloka.get("telugu") if sloka else None,
                }
            )

        title = rules[0]["name"] if len(rules) == 1 else key.replace("_", " ").title()
        summary = (rules[0].get("result") or {}).get("summary") or title
        conclusions.append(
            {
                "conclusion_key": key,
                "title": title,
                "summary": summary,
                "themes": sorted(
                    {
                        t
                        for r in rules
                        for t in (r.get("result") or {}).get("themes", [])
                    }
                ),
                "evidence": uniq_ev,
                "used_rules": [r["rule_id"] for r in rules],
                "rule_details": [
                    {
                        "rule_id": r["rule_id"],
                        "name": r["name"],
                        "priority": r["priority"],
                        "modern_interpretation": r.get("modern_interpretation"),
                        "evidence_checks": r.get("evidence_checks"),
                    }
                    for r in rules
                ],
                "sources": sources,
                "confidence": _confidence(rules),
                "category": rules[0].get("category"),
            }
        )
    conclusions.sort(key=lambda c: (-c["confidence"], c["conclusion_key"]))
    return conclusions


def build_evidence_pack(
    chart: dict,
    category: str | None = None,
    extras: dict | None = None,
    language: str = "en",
) -> dict[str, Any]:
    matched = match_rules(chart, category=category, extras=extras)
    conclusions = group_conclusions(matched)
    disclaimer = {
        "en": DISCLAIMER_EN,
        "mr": DISCLAIMER_MR,
        "hi": DISCLAIMER_HI,
        "gu": DISCLAIMER_GU,
        "kn": DISCLAIMER_KN,
        "ta": DISCLAIMER_TA,
        "te": DISCLAIMER_TE,
    }.get(language, DISCLAIMER_EN)

    return {
        "matched_rule_count": len(matched),
        "conclusion_count": len(conclusions),
        "matched_rules": [
            {
                "rule_id": r["rule_id"],
                "name": r["name"],
                "category": r["category"],
                "confidence_base": r["confidence_base"],
                "source": r.get("source"),
            }
            for r in matched
        ],
        "conclusions": conclusions,
        "pipeline": [
            "astronomy",
            "chart",
            "rule_engine",
            "evidence_engine",
            "ai_explanation",
            "audit",
        ],
        "disclaimer": disclaimer,
    }


def explain_conclusion(pack: dict[str, Any], conclusion_key: str) -> dict[str, Any] | None:
    for c in pack.get("conclusions", []):
        if c["conclusion_key"] == conclusion_key or c["title"] == conclusion_key:
            return c
    # fuzzy: match rule id
    for c in pack.get("conclusions", []):
        if conclusion_key in c.get("used_rules", []):
            return c
    return None
