# =============================================================================
# Expense Tracker — Multi-stage Dockerfile
# =============================================================================

# ── Stage 1: Frontend build ──────────────────────────────────────────────────
FROM node:20-alpine AS frontend-build

WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci --omit=optional

COPY frontend/ .
RUN npm run build

# ── Stage 2: Backend ─────────────────────────────────────────────────────────
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    GUNICORN_BIND=0.0.0.0:8000

WORKDIR /app

# Install system dependencies for psycopg2
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

COPY backend/ .
COPY --from=frontend-build /app/frontend/dist /app/static

EXPOSE 8000

CMD ["gunicorn", "wsgi:app", "--config", "gunicorn.conf.py"]
