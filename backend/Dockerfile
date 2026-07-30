FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Force Swiss Ephemeris inside Linux containers
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir pyswisseph==2.10.3.2

COPY . .

RUN python scripts/fetch_ephemeris.py || true

ENV PYTHONPATH=/app
ENV SE_EPHE_PATH=/app/ephe

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
