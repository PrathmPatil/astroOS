"""Astronomy provider abstraction — Swiss Ephemeris preferred, approx fallback."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.astronomy.planets import PlanetPosition


@dataclass(slots=True)
class HouseBundle:
    system: str
    cusps: list[float]
    ascendant: float
    mc: float
    armc: float
    vertex: float


class AstronomyBackend(Protocol):
    name: str

    def planet(self, jd_ut: float, body: str, ayanamsha: str) -> PlanetPosition: ...

    def houses(
        self,
        jd_ut: float,
        latitude: float,
        longitude: float,
        house_system: str,
        ayanamsha: str,
    ) -> HouseBundle: ...

    def ayanamsha(self, jd_ut: float, name: str) -> float: ...
