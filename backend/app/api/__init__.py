from fastapi import APIRouter

from app.api.routes import (
    ai,
    astroos,
    charts,
    dasha,
    dosha,
    gun_milan,
    health,
    marriage,
    transit,
    yogas,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(charts.router, tags=["charts"])
api_router.include_router(dasha.router, tags=["dasha"])
api_router.include_router(yogas.router, tags=["yogas"])
api_router.include_router(dosha.router, tags=["dosha"])
api_router.include_router(gun_milan.router, tags=["matchmaking"])
api_router.include_router(marriage.router, tags=["marriage"])
api_router.include_router(transit.router, tags=["transit"])
api_router.include_router(ai.router, tags=["ai"])
api_router.include_router(astroos.router)
