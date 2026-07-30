"""AstroOS rule/evidence/explain pipeline tests."""

from app.astroos.knowledge import load_all_rules, load_all_slokas
from app.astroos.pipeline import explain_prediction, run_domain, run_full_analysis
from app.astroos.rule_engine import match_rules
from app.schemas import BirthDetails
from app.services.chart_service import compute_chart


def _birth() -> BirthDetails:
    return BirthDetails(
        name="AstroOS Test",
        year=1990,
        month=8,
        day=15,
        hour=10,
        minute=30,
        latitude=19.076,
        longitude=72.8777,
        timezone="Asia/Kolkata",
        place="Mumbai",
    )


def test_knowledge_and_rules_load():
    assert len(load_all_slokas()) >= 5
    assert len(load_all_rules()) >= 10


def test_rule_matching_and_evidence():
    chart = compute_chart(_birth())
    matched = match_rules(chart, category="yoga")
    assert isinstance(matched, list)
    domain = run_domain(_birth(), category="yoga", language="en")
    assert "evidence_pack" in domain
    assert domain["evidence_pack"]["pipeline"][0] == "astronomy"


def test_full_report_and_explain():
    report = run_full_analysis(_birth(), language="mr")
    assert report["philosophy"]["ai_never_invents"] is True
    assert "files" in report
    assert report["files"]["pdf"]
    # explain first available conclusion if any
    if report["conclusions"]:
        key = report["conclusions"][0]["conclusion_key"]
        exp = explain_prediction(_birth(), key, language="en")
        assert exp["found"] is True
        assert exp["ai_meta"]["invented"] is False
        assert exp["audit"]["verifiability"]["ai_invented"] is False
        assert exp["confidence"] >= 0
