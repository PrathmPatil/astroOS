"""AstroOS pipeline orchestrator — Astronomy→Chart→Rules→Evidence→AI→Audit→Report."""

from __future__ import annotations

from typing import Any

from app.astroos.ai_engine import explain_from_evidence
from app.astroos.audit_engine import build_audit_trail
from app.astroos.evidence_engine import build_evidence_pack, explain_conclusion
from app.astroos.report_engine import generate_report_bundle
from app.astroos.rule_engine import match_rules
from app.schemas import BirthDetails
from app.services.analysis_service import compute_dasha, compute_transit
from app.services.chart_service import compute_chart, compute_vargas, disclaimer_for
from app.jyotish.utils import sign_from_longitude


def _dasha_extras(birth: BirthDetails, chart: dict) -> dict:
    dasha = compute_dasha(birth)
    return {
        "mahadasha": dasha["current_mahadasha"]["lord"],
        "antardasha": dasha["current_antardasha"]["lord"],
        "navamsa_examined": True,
        "dasha": dasha,
    }


def _transit_extras(birth: BirthDetails, chart: dict) -> dict:
    transit = compute_transit(birth)
    lagna = chart["ascendant"]
    lagna_sign = int(sign_from_longitude(lagna).sign_index)

    def house_of(lon: float) -> int:
        return ((int(sign_from_longitude(lon).sign_index) - lagna_sign) % 12) + 1

    transit_houses = {
        t["planet"]: house_of(t["transit_longitude"]) for t in transit["transits"]
    }
    return {"transit_houses": transit_houses, "transit": transit}


def run_domain(
    birth: BirthDetails,
    category: str | None,
    language: str = "mr",
) -> dict[str, Any]:
    chart = compute_chart(birth)
    extras = _dasha_extras(birth, chart)
    if category == "transit":
        extras.update(_transit_extras(birth, chart))

    pack = build_evidence_pack(chart, category=category, extras=extras, language=language)

    # Attach AI explanations (evidence-only) to each conclusion
    for c in pack["conclusions"]:
        ai = explain_from_evidence(c, language=language)
        c["ai_explanation"] = ai["explanation"]
        c["ai_meta"] = {
            "provider": ai["provider"],
            "invented": ai["invented"],
            "inputs_used": ai["inputs_used"],
        }
        c["audit"] = build_audit_trail(c, chart_meta=chart.get("meta"))

    return {
        "meta": chart["meta"],
        "lagna": chart["lagna"],
        "moon": chart["moon"],
        "category": category,
        "language": language,
        "evidence_pack": pack,
        "disclaimer": pack["disclaimer"],
    }


def run_full_analysis(birth: BirthDetails, language: str = "mr") -> dict[str, Any]:
    chart = compute_chart(birth)
    vargas = compute_vargas(birth)
    extras = _dasha_extras(birth, chart)
    extras.update(_transit_extras(birth, chart))

    categories = [
        "yoga",
        "dosha",
        "marriage",
        "career",
        "wealth",
        "health",
        "transit",
        "remedy",
    ]
    by_category = {}
    all_conclusions = []
    for cat in categories:
        pack = build_evidence_pack(chart, category=cat, extras=extras, language=language)
        for c in pack["conclusions"]:
            ai = explain_from_evidence(c, language=language)
            c["ai_explanation"] = ai["explanation"]
            c["ai_meta"] = {
                "provider": ai["provider"],
                "invented": False,
                "inputs_used": ai["inputs_used"],
            }
            c["audit"] = build_audit_trail(c, chart_meta=chart.get("meta"))
            all_conclusions.append(c)
        by_category[cat] = pack

    report = {
        "title": f"AstroOS Report — {birth.name or 'Native'}",
        "meta": chart["meta"],
        "lagna": chart["lagna"],
        "moon": chart["moon"],
        "vargas_available": list((vargas.get("vargas") or {}).keys()),
        "conclusions": all_conclusions,
        "by_category": {k: v["conclusions"] for k, v in by_category.items()},
        "disclaimer": disclaimer_for(language),
        "philosophy": {
            "usp": "Evidence → Rule → Classical Source → AI Explanation → Confidence",
            "ai_never_invents": True,
        },
    }
    paths = generate_report_bundle(
        report,
        stem=f"astroos_{(birth.name or 'native').replace(' ', '_').lower()}",
        language=language if language in {"en", "mr", "hi", "gu", "kn", "ta", "te"} else "en",
    )
    report["files"] = paths
    return report


def explain_prediction(
    birth: BirthDetails,
    conclusion_key: str,
    language: str = "mr",
    category: str | None = None,
) -> dict[str, Any]:
    if category:
        result = run_domain(birth, category=category, language=language)
        conclusions = result["evidence_pack"]["conclusions"]
        meta = result.get("meta")
    else:
        result = run_full_analysis(birth, language=language)
        conclusions = result["conclusions"]
        meta = result.get("meta")

    pack = {"conclusions": conclusions}
    hit = explain_conclusion(pack, conclusion_key)
    if not hit:
        return {
            "found": False,
            "conclusion_key": conclusion_key,
            "message": "No matched conclusion for this key in current rule pack.",
            "available": [c["conclusion_key"] for c in conclusions],
            "disclaimer": disclaimer_for("en"),
        }

    ai = explain_from_evidence(hit, language=language)
    audit = hit.get("audit") or build_audit_trail(hit, chart_meta=meta)

    return {
        "found": True,
        "conclusion_key": hit["conclusion_key"],
        "title": hit["title"],
        "title_localized": ai["title_localized"],
        "summary": hit["summary"],
        "final_conclusion": ai["final_conclusion"],
        "confidence": hit["confidence"],
        "evidence": hit["evidence"],
        "used_rules": hit["used_rules"],
        "rule_details": hit["rule_details"],
        "sources": hit["sources"],
        "classical_views": [
            {
                "book": s.get("text"),
                "sanskrit": s.get("sanskrit"),
                "english": s.get("english"),
                "marathi": s.get("marathi"),
                "hindi": s.get("hindi"),
                "gujarati": s.get("gujarati"),
                "kannada": s.get("kannada"),
                "tamil": s.get("tamil"),
                "telugu": s.get("telugu"),
                "chapter": s.get("chapter"),
            }
            for s in hit.get("sources", [])
        ],
        "ai_explanation": ai["explanation"],
        "ai_meta": {
            "invented": False,
            "provider": ai["provider"],
            "inputs_used": ai["inputs_used"],
        },
        "audit": audit,
        "usp_chain": [
            "final_conclusion",
            "evidence",
            "rule",
            "classical_source",
            "ai_explanation",
            "confidence",
        ],
        "alternative_classical_views": [
            "Schools differ on orbs, ayanamsha, and house systems; AstroOS shows the linked teaching references used for this match.",
            "Confirm with full chart consultation when decisions matter.",
        ],
        "disclaimer": ai["disclaimer"],
    }
