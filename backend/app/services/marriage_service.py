"""Marriage microservice orchestration."""

from __future__ import annotations

from app.jyotish.marriage import analyze_marriage
from app.schemas import BirthDetails
from app.services.analysis_service import compute_dasha, compute_doshas, compute_transit
from app.services.chart_service import compute_chart, disclaimer_for


def marriage_full_report(birth: BirthDetails) -> dict:
    chart = compute_chart(birth)
    analysis = analyze_marriage(chart)
    dasha = compute_dasha(birth)
    doshas = compute_doshas(birth)
    transit = compute_transit(birth)

    manglik = next(
        (d for d in doshas["doshas"] if d["key"] == "manglik"),
        None,
    )

    return {
        "meta": chart["meta"],
        "lagna": chart["lagna"],
        "moon": chart["moon"],
        "seventh_house": analysis.seventh_house,
        "venus": analysis.venus,
        "jupiter": analysis.jupiter,
        "navamsa": analysis.navamsa,
        "karakas": analysis.karakas,
        "timing": {
            "windows": analysis.timing_windows,
            "current_dasha": {
                "mahadasha": dasha["current_mahadasha"],
                "antardasha": dasha["current_antardasha"],
            },
        },
        "love_marriage": analysis.love_marriage,
        "spouse_prediction": analysis.spouse_profile,
        "dosha_flags": {
            "manglik": manglik,
            "present_doshas": [d for d in doshas["doshas"] if d["present"]],
        },
        "transit_snapshot": {
            "at": transit["at"],
            "key_planets": [
                t
                for t in transit["transits"]
                if t["planet"] in {"Jupiter", "Saturn", "Rahu", "Ketu", "Venus"}
            ],
        },
        "summary": analysis.summary,
        "disclaimer": disclaimer_for("en"),
    }


def marriage_timing_only(birth: BirthDetails) -> dict:
    data = marriage_full_report(birth)
    return {
        "meta": data["meta"],
        "timing": data["timing"],
        "summary": data["summary"],
        "disclaimer": data["disclaimer"],
    }


def marriage_spouse_only(birth: BirthDetails) -> dict:
    data = marriage_full_report(birth)
    return {
        "meta": data["meta"],
        "spouse_prediction": data["spouse_prediction"],
        "karakas": data["karakas"],
        "navamsa": {
            "d9_lagna": data["navamsa"].get("d9_lagna"),
            "d9_seventh": data["navamsa"].get("d9_seventh"),
        },
        "disclaimer": data["disclaimer"],
    }


def marriage_love_only(birth: BirthDetails) -> dict:
    data = marriage_full_report(birth)
    return {
        "meta": data["meta"],
        "love_marriage": data["love_marriage"],
        "disclaimer": data["disclaimer"],
    }
