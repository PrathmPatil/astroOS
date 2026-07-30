"""Smoke tests for core calculation engine."""

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from app.jyotish.gun_milan import gun_milan
from app.jyotish.utils import nakshatra_from_longitude, sign_from_longitude
from app.jyotish.vargas import varga_longitude
from app.schemas import BirthDetails
from app.services.chart_service import compute_chart
from app.services.analysis_service import (
    compute_dasha,
    compute_doshas,
    compute_yogas,
)


@pytest.fixture
def sample_birth() -> BirthDetails:
    # Example: Mumbai
    return BirthDetails(
        name="Test Native",
        year=1990,
        month=8,
        day=15,
        hour=10,
        minute=30,
        second=0,
        latitude=19.0760,
        longitude=72.8777,
        timezone="Asia/Kolkata",
        place="Mumbai",
    )


def test_sign_and_nakshatra_helpers():
    sp = sign_from_longitude(45.5)
    assert sp.sign == "Taurus"
    nak = nakshatra_from_longitude(45.5)
    assert nak.name
    assert 1 <= nak.pada <= 4


def test_navamsa_mapping():
    # Longitude in Aries 2° → first navamsa of Aries path
    lon = varga_longitude(2.0, "D9")
    assert 0 <= lon < 360


def test_birth_chart(sample_birth: BirthDetails):
    chart = compute_chart(sample_birth)
    assert chart["lagna"]["sign"]
    assert len(chart["planets"]) >= 9
    assert len(chart["houses"]) == 12
    names = {p["name"] for p in chart["planets"]}
    assert {"Sun", "Moon", "Rahu", "Ketu"}.issubset(names)


def test_dasha_yogas_doshas(sample_birth: BirthDetails):
    dasha = compute_dasha(sample_birth)
    assert dasha["current_mahadasha"]["lord"]
    yogas = compute_yogas(sample_birth)
    assert len(yogas["yogas"]) > 0
    doshas = compute_doshas(sample_birth)
    assert len(doshas["doshas"]) > 0


def test_gun_milan():
    # Two sample moon longitudes
    result = gun_milan(40.0, 120.0)
    assert result.maximum == 36
    assert 0 <= result.total <= 36
    assert len(result.kootas) == 8
