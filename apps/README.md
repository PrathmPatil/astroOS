# AstroOS monorepo layout

Runtime code currently lives in `backend/` and `frontend/`.

This `apps/` + `packages/` tree is the target layout:

| Path | Maps to |
|------|---------|
| `apps/api` | `backend/` (FastAPI AstroOS API) |
| `apps/web` | `frontend/` |
| `apps/admin` | Admin console (scaffold) |
| `packages/*` | Logical engines under `backend/app/astroos` + `backend/app/jyotish` |
| `knowledge/` | Classical text packs |
| `rules/` | YAML rule packs |
| `docker/` | Compose overlays |

Until full physical migration, import paths remain `app.*` inside `backend/`.
