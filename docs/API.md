# AstroOS API

Base: `/api/v1`

## Core AstroOS

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/astroos/rules` | List YAML rules |
| GET | `/astroos/knowledge` | List classical sloka pack |
| POST | `/charts` | D1 + Vargas + house systems |
| POST | `/planets` | Astronomy snapshot + shadbala scaffold |
| POST | `/houses` | Houses |
| POST | `/dasha` | Vimshottari |
| POST | `/navamsa` | D9 |
| POST | `/yogas` | Evidence-backed yogas |
| POST | `/doshas` | Evidence-backed doshas |
| POST | `/transits` | Evidence-backed transits |
| POST | `/marriage` | Evidence + classic marriage |
| POST | `/compatibility` | Gun Milan + modern |
| POST | `/career` | Career evidence |
| POST | `/wealth` | Wealth evidence |
| POST | `/remedies` | Sourced remedies |
| POST | `/evidence` | Full evidence report + files |
| POST | `/report` | Same as evidence (multi-format files) |
| POST | `/audit` | Audit a conclusion |
| POST | `/evidence/explain` | **Explain Every Prediction (USP)** |

## Legacy AstroSutra routes

Still available: `/birth-chart`, `/gun-milan`, `/matchmaking`, `/marriage/overview`, …

## Explain body

```json
{
  "birth": { "year": 1990, "month": 8, "day": 15, "hour": 10, "minute": 30, "latitude": 19.07, "longitude": 72.87, "timezone": "Asia/Kolkata" },
  "conclusion_key": "marriage_delay",
  "language": "mr"
}
```
