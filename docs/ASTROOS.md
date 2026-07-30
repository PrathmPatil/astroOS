# AstroOS Architecture

## USP

**Evidence → Rule → Classical Source → AI Explanation → Confidence**

AI never invents planetary facts or definite predictions.

## Layers

1. Astronomy Engine — Swiss Ephemeris / approx fallback, dignity, nakshatra, full Shadbala components  
2. Chart Engine — Vargas D1–D60; house systems W / E / P / KP / Sripati  
3. Rule Engine — YAML rules in `/rules` (core + extended packs)  
4. Evidence Engine — groups matched rules into conclusions with confidence  
5. AI Engine — evidence-only explainer (en/mr/hi/gu/kn/ta/te)  
6. Report Engine — PDF / Word (docx) / HTML / Markdown / JSON  
7. Marriage Engine — classic + evidence layer  
8. Compatibility Engine — 36 guna + 13 modern dimensions (incl. attachment/lifestyle/conflict)  
9. Career Engine — evidence-backed career themes  
10. Transit Engine — daily/weekly/monthly/yearly + Sa/Ju/Ra/Ke slow-planet focus  
11. Remedy Engine — sourced remedies with limitations  
12. Audit Engine — full verification chain (prediction → evidence → rules → planets/houses → sloka → AI)  

## Knowledge

`/knowledge/{bphs,phaladeepika,saravali,jataka_parijata,brihat_jataka}` — multi-language slokas

## Rules

`/rules/{yogas,doshas,marriage,career,wealth,health,transit,remedies}` (+ `extended.yaml`)

## Monorepo map

`apps/{api,web,admin}` + `packages/*` point at current `backend/` / `frontend/` until full migration.

## Explain API

`POST /api/v1/evidence/explain`
