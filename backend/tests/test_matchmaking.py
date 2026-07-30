"""Gun Milan + advanced compatibility tests."""

from app.schemas import BirthDetails, GunMilanRequest
from app.services.matchmaking_service import (
    compute_gun_milan_enriched,
    kundali_matching,
)


def _pair() -> GunMilanRequest:
    return GunMilanRequest(
        boy=BirthDetails(
            name="Rahul",
            year=1990,
            month=8,
            day=15,
            hour=10,
            minute=30,
            latitude=19.076,
            longitude=72.8777,
            timezone="Asia/Kolkata",
            place="Mumbai",
        ),
        girl=BirthDetails(
            name="Priya",
            year=1992,
            month=3,
            day=21,
            hour=14,
            minute=15,
            latitude=18.5204,
            longitude=73.8567,
            timezone="Asia/Kolkata",
            place="Pune",
        ),
    )


def test_gun_milan_enriched():
    data = compute_gun_milan_enriched(_pair())
    assert data["maximum"] == 36
    assert len(data["kootas"]) == 8
    assert "strengths" in data
    assert "weaknesses" in data
    assert "dosha_checks" in data


def test_kundali_matching_modes():
    data = kundali_matching(_pair())
    assert len(data["modern"]["dimensions"]) == 13
    assert {"attachment", "lifestyle", "conflict"}.issubset(
        {d["key"] for d in data["modern"]["dimensions"]}
    )
    assert data["modern"]["why_summary"]
    assert "ai_combined" in data
    assert 0 <= data["modes"]["ai_combined_score"] <= 100
    assert data["traditional"]["boy_nakshatra"]
    assert data["ai_combined"]["narrative"]
