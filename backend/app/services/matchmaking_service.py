"""Kundali matching: traditional Gun Milan + advanced + AI-combined."""

from __future__ import annotations

from app.jyotish.compatibility import advanced_compatibility
from app.jyotish.doshas import detect_doshas
from app.jyotish.gun_milan import gun_milan
from app.schemas import GunMilanRequest
from app.services.chart_service import compute_chart, disclaimer_for


def _strengths_weaknesses(kootas: list[dict]) -> tuple[list[str], list[str]]:
    strengths: list[str] = []
    weaknesses: list[str] = []
    for k in kootas:
        ratio = k["obtained"] / k["maximum"] if k["maximum"] else 0
        label = f"{k['name']} ({k['obtained']:g}/{k['maximum']:g})"
        if ratio >= 0.75:
            strengths.append(label)
        elif ratio <= 0.35:
            weaknesses.append(label)
    return strengths, weaknesses


def _traditional_block(boy: dict, girl: dict) -> dict:
    result = gun_milan(boy["positions"]["Moon"], girl["positions"]["Moon"])
    kootas = [
        {
            "name": k.name,
            "obtained": k.obtained,
            "maximum": k.maximum,
            "notes": k.notes,
            "ratio": round(k.obtained / k.maximum, 3) if k.maximum else 0,
        }
        for k in result.kootas
    ]
    strengths, weaknesses = _strengths_weaknesses(kootas)

    boy_doshas = detect_doshas(boy["positions"], boy["ascendant"])
    girl_doshas = detect_doshas(girl["positions"], girl["ascendant"])
    boy_manglik = next(d for d in boy_doshas if d.key == "manglik")
    girl_manglik = next(d for d in girl_doshas if d.key == "manglik")

    nadi = next(k for k in kootas if k["name"] == "Nadi")
    bhakut = next(k for k in kootas if k["name"] == "Bhakut")

    return {
        "total": result.total,
        "maximum": result.maximum,
        "percentage": result.percentage,
        "verdict": result.verdict,
        "kootas": kootas,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "boy_nakshatra": result.boy_nakshatra,
        "girl_nakshatra": result.girl_nakshatra,
        "boy_rasi": result.boy_rasi,
        "girl_rasi": result.girl_rasi,
        "dosha_checks": {
            "nadi_dosha": nadi["obtained"] == 0,
            "bhakut_dosha": bhakut["obtained"] == 0,
            "boy_manglik": boy_manglik.present,
            "girl_manglik": girl_manglik.present,
            "manglik_balance": boy_manglik.present == girl_manglik.present,
        },
    }


def _ai_combined(traditional: dict, modern: dict) -> dict:
    """Blend Ashtakoot (60%) with advanced dimensions (40%)."""
    t = traditional["percentage"]
    m = modern["overall_score"]
    blended = round(0.6 * t + 0.4 * m, 2)

    if blended >= 75:
        verdict = "Strong combined match"
    elif blended >= 58:
        verdict = "Favourable combined match"
    elif blended >= 45:
        verdict = "Mixed - weigh specific kootas & dimensions"
    else:
        verdict = "Cautious - deeper chart consultation advised"

    highlights = []
    if traditional["strengths"]:
        highlights.append("Traditional strengths: " + ", ".join(traditional["strengths"][:3]))
    if traditional["weaknesses"]:
        highlights.append("Watch: " + ", ".join(traditional["weaknesses"][:3]))
    top_dims = sorted(modern["dimensions"], key=lambda d: d["score"], reverse=True)[:3]
    highlights.append(
        "Strong modern dimensions: " + ", ".join(f"{d['label']} ({d['score']})" for d in top_dims)
    )
    weak_dims = sorted(modern["dimensions"], key=lambda d: d["score"])[:2]
    highlights.append(
        "Softer modern dimensions: " + ", ".join(f"{d['label']} ({d['score']})" for d in weak_dims)
    )

    flags = []
    checks = traditional["dosha_checks"]
    if checks["nadi_dosha"]:
        flags.append("Nadi dosha flagged in Ashtakoot — classical caution")
    if checks["bhakut_dosha"]:
        flags.append("Bhakut dosha flagged — review longevity/harmony themes")
    if checks["boy_manglik"] or checks["girl_manglik"]:
        if checks["manglik_balance"]:
            flags.append("Manglik pattern present on both sides (often read as balancing)")
        else:
            flags.append("Uneven Manglik pattern — traditional texts advise extra care")

    return {
        "score": blended,
        "verdict": verdict,
        "weights": {"traditional_percent": 60, "modern_percent": 40},
        "highlights": highlights,
        "flags": flags,
        "narrative": (
            f"Traditional Ashtakoot scored {t}/100 ({traditional['verdict']}). "
            f"Modern dimensional score {m}/100 ({modern['overall_band']}). "
            f"Combined index {blended}/100 — {verdict}. "
            "This is a rule-engine blend of classical and modern Jyotish indicators, "
            "not an AI hallucination and not a scientific prediction."
        ),
    }


def kundali_matching(payload: GunMilanRequest) -> dict:
    boy = compute_chart(payload.boy)
    girl = compute_chart(payload.girl)
    traditional = _traditional_block(boy, girl)
    modern = advanced_compatibility(boy, girl)
    combined = _ai_combined(traditional, modern)

    return {
        "profiles": {
            "boy": {
                "name": payload.boy.name,
                "lagna": boy["lagna"],
                "moon": boy["moon"],
            },
            "girl": {
                "name": payload.girl.name,
                "lagna": girl["lagna"],
                "moon": girl["moon"],
            },
        },
        "traditional": traditional,
        "modern": modern,
        "ai_combined": combined,
        "modes": {
            "traditional_score": traditional["percentage"],
            "modern_score": modern["overall_score"],
            "ai_combined_score": combined["score"],
        },
        "disclaimer": disclaimer_for("en"),
    }


def compute_gun_milan_enriched(payload: GunMilanRequest) -> dict:
    """Keep /gun-milan response shape while adding strengths/weaknesses."""
    full = kundali_matching(payload)
    t = full["traditional"]
    return {
        "total": t["total"],
        "maximum": t["maximum"],
        "percentage": t["percentage"],
        "verdict": t["verdict"],
        "kootas": [
            {
                "name": k["name"],
                "obtained": k["obtained"],
                "maximum": k["maximum"],
                "notes": k["notes"],
            }
            for k in t["kootas"]
        ],
        "boy_nakshatra": t["boy_nakshatra"],
        "girl_nakshatra": t["girl_nakshatra"],
        "boy_rasi": t["boy_rasi"],
        "girl_rasi": t["girl_rasi"],
        "strengths": t["strengths"],
        "weaknesses": t["weaknesses"],
        "dosha_checks": t["dosha_checks"],
        "disclaimer": full["disclaimer"],
    }
