from fastapi import APIRouter

from app.ai.provider import generate_analysis
from app.schemas import AIAnalysisRequest, AIAnalysisResponse
from app.services.analysis_service import compute_dasha, compute_doshas, compute_yogas
from app.services.chart_service import compute_chart, disclaimer_for

router = APIRouter()


@router.post("/ai-analysis", response_model=AIAnalysisResponse)
async def ai_analysis(payload: AIAnalysisRequest) -> AIAnalysisResponse:
    chart = compute_chart(payload.birth)
    dasha = compute_dasha(payload.birth)
    yogas = compute_yogas(payload.birth)
    doshas = compute_doshas(payload.birth)

    summary = {
        "lagna": chart["lagna"],
        "moon": chart["moon"],
        "planets": [
            {
                "name": p["name"],
                "sign": p["sign"],
                "house": p["house"],
                "nakshatra": p["nakshatra"],
                "retrograde": p["retrograde"],
            }
            for p in chart["planets"]
            if p["name"]
            in {
                "Sun",
                "Moon",
                "Mars",
                "Mercury",
                "Jupiter",
                "Venus",
                "Saturn",
                "Rahu",
                "Ketu",
            }
        ],
        "current_dasha": {
            "mahadasha": dasha["current_mahadasha"]["lord"],
            "antardasha": dasha["current_antardasha"]["lord"],
        },
        "yogas_present": [y["name"] for y in yogas["yogas"] if y["present"]],
        "doshas_present": [d["name"] for d in doshas["doshas"] if d["present"]],
    }

    text, provider = await generate_analysis(
        payload.language, payload.focus, summary
    )
    return AIAnalysisResponse(
        language=payload.language,
        focus=payload.focus,
        analysis=text,
        provider=provider,
        chart_summary=summary,
        disclaimer=disclaimer_for(payload.language),
    )
