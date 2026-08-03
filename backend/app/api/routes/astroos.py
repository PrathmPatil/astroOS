"""AstroOS API routes — charts, evidence, audit, domains, report."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.astroos.chart_layer import astronomy_snapshot, chart_engine_bundle
from app.astroos.knowledge import load_all_rules, load_all_slokas
from app.astroos.pipeline import explain_prediction, run_domain, run_full_analysis
from app.astroos.transit_engine import transit_periods
from app.schemas import BirthDetails, GunMilanRequest
from app.services.analysis_service import compute_dasha
from app.services.chart_service import compute_chart, compute_vargas
from app.services.matchmaking_service import kundali_matching
from app.services.marriage_service import marriage_full_report

router = APIRouter(tags=["astroos"])


class ExplainRequest(BaseModel):
    birth: BirthDetails
    conclusion_key: str = Field(..., examples=["marriage_delay", "YOGA_001", "career_strong"])
    language: Literal["en", "mr", "hi", "gu", "kn", "ta", "te"] = "mr"
    category: str | None = None


class DomainRequest(BaseModel):
    birth: BirthDetails
    language: Literal["en", "mr", "hi", "gu", "kn", "ta", "te"] = "mr"


@router.get("/astroos/rules")
def list_rules():
    rules = load_all_rules()
    return {"count": len(rules), "rules": [{"rule_id": r["rule_id"], "name": r["name"], "category": r.get("category"), "source": r.get("source")} for r in rules]}


@router.get("/astroos/knowledge")
def list_knowledge():
    slokas = load_all_slokas()
    return {"count": len(slokas), "slokas": list(slokas.values())}


@router.post("/charts")
def charts(payload: BirthDetails):
    return chart_engine_bundle(payload)


@router.post("/planets")
def planets_os(payload: BirthDetails):
    return astronomy_snapshot(payload)


@router.post("/houses")
def houses_os(payload: BirthDetails):
    chart = compute_chart(payload)
    return {"houses": chart["houses"], "lagna": chart["lagna"], "house_system": chart["meta"]["house_system"]}


@router.post("/dasha")
def dasha_os(payload: BirthDetails):
    return compute_dasha(payload)


@router.post("/navamsa")
def navamsa_os(payload: BirthDetails):
    v = compute_vargas(payload)
    return {"d9": v["vargas"].get("D9", []), "meta": v["meta"], "disclaimer": v["disclaimer"]}


@router.post("/yogas")
def yogas_os(payload: DomainRequest):
    return run_domain(payload.birth, category="yoga", language=payload.language)


@router.post("/doshas")
def doshas_os(payload: DomainRequest):
    return run_domain(payload.birth, category="dosha", language=payload.language)


@router.post("/transits")
def transits_os(payload: DomainRequest):
    evidence = run_domain(payload.birth, category="transit", language=payload.language)
    periods = transit_periods(payload.birth)
    return {"evidence_layer": evidence, "periods": periods}


@router.post("/marriage")
def marriage_os(payload: DomainRequest):
    evidence = run_domain(payload.birth, category="marriage", language=payload.language)
    classic = marriage_full_report(payload.birth)
    return {"evidence_layer": evidence, "classic_layer": classic}


@router.post("/compatibility")
def compatibility_os(payload: GunMilanRequest):
    return kundali_matching(payload)


@router.post("/career")
def career_os(payload: DomainRequest):
    return run_domain(payload.birth, category="career", language=payload.language)


@router.post("/wealth")
def wealth_os(payload: DomainRequest):
    return run_domain(payload.birth, category="wealth", language=payload.language)


@router.post("/remedies")
def remedies_os(payload: DomainRequest):
    return run_domain(payload.birth, category="remedy", language=payload.language)


@router.post("/evidence")
def evidence_os(payload: DomainRequest):
    # Avoid report file I/O on serverless; conclusions still returned
    return run_full_analysis(
        payload.birth, language=payload.language, write_reports=False
    )


@router.post("/report")
def report_os(payload: DomainRequest):
    return run_full_analysis(payload.birth, language=payload.language, write_reports=True)


@router.post("/audit")
def audit_os(payload: ExplainRequest):
    return explain_prediction(
        payload.birth,
        payload.conclusion_key,
        language=payload.language,
        category=payload.category,
    )


@router.post("/evidence/explain")
def explain_os(payload: ExplainRequest):
    """Explain Every Prediction — USP endpoint."""
    return explain_prediction(
        payload.birth,
        payload.conclusion_key,
        language=payload.language,
        category=payload.category,
    )
