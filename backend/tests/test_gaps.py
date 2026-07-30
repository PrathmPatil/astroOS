"""AstroOS gap-closure tests: shadbala, houses, transit, languages, scale."""

from app.astroos.chart_layer import astronomy_snapshot, chart_engine_bundle
from app.astroos.knowledge import load_all_rules, load_all_slokas
from app.astroos.pipeline import run_full_analysis
from app.astroos.report_engine import SUPPORTED_LANGS, generate_report_bundle
from app.astroos.transit_engine import transit_periods
from app.astronomy.house_systems import HOUSE_SYSTEMS
from app.schemas import BirthDetails


def _birth() -> BirthDetails:
    return BirthDetails(
        name="Gap Test",
        year=1990,
        month=8,
        day=15,
        hour=10,
        minute=30,
        latitude=19.076,
        longitude=72.8777,
        timezone="Asia/Kolkata",
    )


def test_shadbala_and_house_systems():
    snap = astronomy_snapshot(_birth())
    sun = next(p for p in snap["planets"] if p["name"] == "Sun")
    assert "sthana_bala" in sun["shadbala"]
    assert "total" in sun["shadbala"]
    assert sun["shadbala"]["total"] > 0
    bundle = chart_engine_bundle(_birth())
    assert set(HOUSE_SYSTEMS).issubset(set(bundle["house_systems"]))
    assert "KP" in bundle["house_systems"]
    assert "S" in bundle["house_systems"]


def test_rules_and_slokas_scaled():
    assert len(load_all_rules()) >= 30
    assert len(load_all_slokas()) >= 14


def test_transit_periods():
    data = transit_periods(_birth())
    assert set(data["periods"]) == {"daily", "weekly", "monthly", "yearly"}
    assert "Saturn" in data["slow_planets"]
    assert "Jupiter" in data["slow_planets"]


def test_report_docx_and_langs():
    report = run_full_analysis(_birth(), language="en")
    assert "docx" in report["files"]
    assert set(SUPPORTED_LANGS) == {"en", "mr", "hi", "gu", "kn", "ta", "te"}
    paths = generate_report_bundle(report, stem="gap_lang_mr", language="mr")
    assert paths["language"] == "mr"
