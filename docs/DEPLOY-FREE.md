# Free forever hosting (no Fly.io)

AstroOS splits into two free services:

| Part | Platform | Free URL |
|------|----------|----------|
| Frontend (Next.js) | [Vercel](https://vercel.com) Hobby | `https://….vercel.app` |
| Backend (FastAPI) | [Render](https://render.com) Free | `https://….onrender.com` |

Both free tiers are ongoing (not a one-month trial). Limits: Render sleeps after idle (~15 min); first request can take 30–60s.

---

## 0. Push code to GitHub

```powershell
cd C:\Users\PRATHMESH\Projects\astrosutra-ai
git remote -v
# If no remote yet: create a GitHub repo, then:
# git remote add origin https://github.com/YOUR_USER/astrosutra-ai.git
git add .
git commit -m "Prepare free Vercel + Render deploy"
git push -u origin HEAD
```

---

## 1. Deploy API on Render (free)

1. Open https://dashboard.render.com → sign up with GitHub  
2. **New** → **Blueprint** → connect `astrosutra-ai`  
   - Or **New** → **Web Service** → repo → Docker  
   - Root directory: leave empty (repo root)  
   - Dockerfile: `Dockerfile.api`  
3. Plan: **Free**  
4. After deploy, copy URL, e.g. `https://astroos-api.onrender.com`  
5. Check: `https://astroos-api.onrender.com/api/v1/health`

---

## 2. Deploy Web on Vercel (free)

1. Open https://vercel.com → sign up with GitHub  
2. **Add New Project** → import `astrosutra-ai`  
3. Settings:
   - **Root Directory:** `frontend`  
   - **Framework:** Next.js  
4. Environment variable:

   | Name | Value |
   |------|--------|
   | `NEXT_PUBLIC_API_URL` | `https://YOUR-API.onrender.com/api/v1` |

5. Deploy → open `https://YOUR-APP.vercel.app`

---

## 3. Wire CORS

In Render → astroos-api → Environment → set:

```text
CORS_ORIGINS=https://YOUR-APP.vercel.app
```

(API also allows `*.vercel.app` / `*.onrender.com` via regex.)

Redeploy API if needed.

---

## Local test against free API

```powershell
# frontend/.env.local
NEXT_PUBLIC_API_URL=https://YOUR-API.onrender.com/api/v1
```

---

## Optional: both on Render

You can also host the Next app as a second Render Web Service with `Dockerfile.web` (Free plan). Vercel is usually faster for Next.js.

---

## Not using Fly.io

Fly requires a working `flyctl auth login` browser session. Use Vercel + Render instead for click-deploy with GitHub.
