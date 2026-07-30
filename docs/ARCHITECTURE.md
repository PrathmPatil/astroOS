# AstroSutra AI — Architecture

## Design Goals

- Enterprise-ready, module-based, testable
- Clear separation: **Astronomy → Rules → AI**
- SaaS / API / Mobile-ready from day one
- Every interpretation carries a traditional-astrology disclaimer

## Layer Diagram

```
┌─────────────────────────────────────────────────────────┐
│  Clients: Web · Mobile · WhatsApp · Telegram · Voice    │
└───────────────────────────┬─────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────┐
│  API Gateway (FastAPI) + Auth + Rate Limits + Admin     │
└───────┬─────────────────┬─────────────────┬─────────────┘
        │                 │                 │
┌───────▼───────┐ ┌───────▼───────┐ ┌───────▼───────┐
│ AI Layer      │ │ Jyotish Rules │ │ Reports/PDF   │
│ Prompt Engine │ │ Yogas/Doshas  │ │ Celery Jobs   │
│ RAG / LLM     │ │ Dasha/Milan   │ │ Storage       │
└───────┬───────┘ └───────┬───────┘ └───────┬───────┘
        │                 │                 │
        └────────────┬────┴─────────────────┘
                     │
           ┌─────────▼─────────┐
           │ Astronomy Layer   │
           │ Swiss Ephemeris   │
           │ Sidereal / Houses │
           └─────────┬─────────┘
                     │
           ┌─────────▼─────────┐
           │ PostgreSQL + Redis│
           └───────────────────┘
```

## Backend Packages

| Package | Responsibility |
|---------|----------------|
| `app.astronomy` | JD conversion, planets, houses, ayanamsha |
| `app.jyotish` | Signs, nakshatras, vargas, yogas, doshas, dasha, gun milan |
| `app.ai` | Prompt engine, providers (OpenAI/Ollama), disclaimers |
| `app.api` | Versioned HTTP routes |
| `app.models` | ORM + Pydantic schemas |
| `app.services` | Orchestration across layers |
| `app.workers` | Celery PDF / long analysis jobs |

## Ayanamsha

Default: **Lahiri (Chitrapaksha)** — configurable via request / settings.

## House System

Default for Vedic whole-sign analysis: **Whole Sign** (`W`).  
Placidus / Equal available as options for research modes.

## Marriage Module

Planned as a dedicated service package (`app.services.marriage`) with its own routes under `/api/v1/marriage/*`, so it can later extract to a true microservice without rewriting domain logic.

## Scaling Path

1. **Phase 1** — Core chart + dasha + yogas + gun milan (current scaffold)
2. **Phase 2** — Full Vargas D1–D60, all doshas, transit engine
3. **Phase 3** — AI RAG + multilingual reports + PDF
4. **Phase 4** — SaaS billing, admin analytics, mobile bots
