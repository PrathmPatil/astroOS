"""Marriage module tests."""

from app.schemas import BirthDetails
from app.services.marriage_service import (
    marriage_full_report,
    marriage_love_only,
    marriage_spouse_only,
    marriage_timing_only,
)


def _birth() -> BirthDetails:
    return BirthDetails(
        name="Marriage Test",
        year=1992,
        month=3,
        day=21,
        hour=14,
        minute=15,
        latitude=18.5204,
        longitude=73.8567,
        timezone="Asia/Kolkata",
        place="Pune",
    )


def test_marriage_full_report():
    data = marriage_full_report(_birth())
    assert data["seventh_house"]["lord"]
    assert data["venus"]["name"] == "Venus"
    assert "windows" in data["timing"]
    assert "probability_score" in data["love_marriage"]
    assert "nature" in data["spouse_prediction"]
    assert data["karakas"]["atmakaraka"]["planet"]
    assert data["karakas"]["darakaraka"]["planet"]
    assert data["navamsa"]["d9_lagna"]["sign"]


def test_marriage_partial_endpoints():
    b = _birth()
    timing = marriage_timing_only(b)
    spouse = marriage_spouse_only(b)
    love = marriage_love_only(b)
    assert "timing" in timing
    assert "spouse_prediction" in spouse
    assert love["love_marriage"]["band"]
