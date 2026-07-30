# Setup notes

## Windows + Swiss Ephemeris

`pyswisseph` needs Microsoft C++ Build Tools on Windows. Until installed (or until you run the API in Docker), AstroSutra automatically uses `approximate_dev` for local wiring.

For production accuracy:

1. Install [Build Tools for Visual Studio](https://visualstudio.microsoft.com/visual-cpp-build-tools/) with the C++ workload, then `pip install pyswisseph==2.10.3.2`
2. Or run `docker compose up api --build`
3. Download ephemeris files:

```bash
cd backend
python scripts/fetch_ephemeris.py
```

## Recommended first ephemeris files

- `seas_18.se1`
- `semo_18.se1`
- `sepl_18.se1`

Source: https://www.astro.com/ftp/swisseph/ephe/

## Marriage module

```bash
curl -X POST http://127.0.0.1:8000/api/v1/marriage/overview \
  -H "Content-Type: application/json" \
  -d "{\"year\":1992,\"month\":3,\"day\":21,\"hour\":14,\"minute\":15,\"latitude\":18.52,\"longitude\":73.85,\"timezone\":\"Asia/Kolkata\"}"
```
