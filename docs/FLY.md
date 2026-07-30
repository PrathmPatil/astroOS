# Deploy AstroOS to Fly.io

Free URLs after deploy:

- API: https://astroos-api.fly.dev
- Web: https://astroos-web.fly.dev

## 1. Install flyctl (Windows PowerShell)

```powershell
iwr https://fly.io/install.ps1 -useb | iex
# Restart terminal, then:
flyctl version
flyctl auth login
```

## 2. Create apps (first time only)

From repo root `astrosutra-ai/`:

```powershell
flyctl apps create astroos-api
flyctl apps create astroos-web
```

If names are taken, edit `app = "..."` in `fly.api.toml` / `fly.web.toml` and use your names everywhere below.

## 3. Deploy API

```powershell
flyctl deploy --config fly.api.toml
flyctl secrets set --config fly.api.toml SECRET_KEY="replace-with-long-random-string"
```

Optional: set CORS after web is live:

```powershell
flyctl secrets set --config fly.api.toml CORS_ORIGINS="https://astroos-web.fly.dev,http://localhost:3001"
```

(Or keep `CORS_ORIGINS` in `fly.api.toml` `[env]`.)

Health check: https://astroos-api.fly.dev/api/v1/health

## 4. Deploy Web

```powershell
flyctl deploy --config fly.web.toml
```

If you renamed the API app:

```powershell
flyctl deploy --config fly.web.toml --build-arg NEXT_PUBLIC_API_URL=https://YOUR-API.fly.dev/api/v1
```

## 5. Open

```powershell
flyctl open --config fly.web.toml
```

## Notes

- Free allowance uses **shared-cpu-1x / 512MB** and **auto-stop** (cold start ~10–30s).
- Region default: `sin` (Singapore). Change `primary_region` in both tomls if you prefer (`bom` Mumbai when available on your plan).
- No Postgres required for current AstroOS features.
- Ephemeris files download during API image build.

## Useful commands

```powershell
flyctl status --config fly.api.toml
flyctl logs --config fly.api.toml
flyctl status --config fly.web.toml
flyctl logs --config fly.web.toml
```

Or one-shot: `.\scripts\deploy-fly.ps1` (after `flyctl auth login`).
