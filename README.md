# AstroOS

**Open Source AI-Powered Vedic Astrology Operating System**

> Not just a horoscope generator — an auditable astrology OS.
>
> **USP:** Evidence → Rule → Classical Source → AI Explanation → Confidence

## Golden Rule (Non-Negotiable)

AI **never** invents predictions. It only explains matched evidence + classical rules.

## Pipeline

```
Astronomy → Chart → Rule Engine → Evidence Engine → AI Explanation → Report / Audit
```

## Monorepo

| Path | Role |
|------|------|
| `backend/` | FastAPI AstroOS API |
| `frontend/` | Web app + Explain Prediction UI |
| `knowledge/` | Classical text excerpts (BPHS, Phaladeepika, …) |
| `rules/` | YAML rule packs (yogas, marriage, career, …) |
| `docs/` | Architecture & API |

## Quick Start

```bash
# API
cd backend
python -m uvicorn app.main:app --reload --port 8000

# Web
cd frontend
npm run dev -- -p 3001
```

- App: http://localhost:3001
- API docs: http://127.0.0.1:8000/docs
- Explain: http://localhost:3001/#explain

## Deploy (free forever)

**Recommended:** Vercel (web) + Render (API) — see [docs/DEPLOY-FREE.md](docs/DEPLOY-FREE.md).

1. Push this repo to GitHub  
2. Render → Web Service / Blueprint → `Dockerfile.api` (Free)  
3. Vercel → import → Root Directory `frontend` → set `NEXT_PUBLIC_API_URL`  

Fly.io configs remain in-repo but are optional (`docs/FLY.md`).

## Layers

1. Astronomy Engine  
2. Chart Engine  
3. Rule Engine  
4. Evidence Engine (**USP**)  
5. AI Engine (explain-only)  
6. Report Generator  
7. Marriage Engine  
8. Compatibility Engine  
9. Career Engine  
10. Transit Engine  
11. Remedy Engine  
12. Audit Engine  

## Disclaimer

Outputs are traditional Vedic interpretive analysis for education/culture — **not** scientifically proven predictions, medical, financial, or legal advice.
