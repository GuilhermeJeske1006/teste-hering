# syntax=docker/dockerfile:1.7
# Monolito da Mesa de Alocação: build do React + FastAPI num único processo (ADR 0002).

FROM node:22-slim AS frontend
WORKDIR /src/frontend
COPY frontend/package.json frontend/package-lock.json frontend/.npmrc ./
RUN npm ci --no-audit --no-fund
COPY frontend/ ./
# O vite.config.ts gera o build em ../backend/app/static
RUN npm run build

FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    MESA_DB_PATH=/data/mesa.db
WORKDIR /app/backend
COPY backend/pyproject.toml ./
COPY backend/app ./app
RUN pip install -e . \
    && useradd --create-home --uid 10001 mesa \
    && mkdir -p /data && chown mesa:mesa /data
COPY --from=frontend /src/backend/app/static ./app/static
USER mesa
EXPOSE 8000
VOLUME ["/data"]
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=4)"
# ANTHROPIC_API_KEY entra em tempo de execução (docker run -e / --env-file), nunca na imagem.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
