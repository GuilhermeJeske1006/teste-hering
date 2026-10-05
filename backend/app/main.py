"""Monolito: FastAPI serve a API em /api e o build do React em / (ADR 0002).

Rode a partir de backend/: `uvicorn app.main:app --port 8000`.
"""
from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, Response

from app.api.errors import register_error_handlers
from app.api.routers import assistants, catalog, exceptions, summary
from app.container import Container, build_container

STATIC_DIR = Path(__file__).resolve().parent / "static"
MISSING_BUILD = ("<!doctype html><html lang='pt-BR'><meta charset='utf-8'><title>Mesa de Alocação</title>"
                 "<p>O build do frontend não foi encontrado. Rode <code>make build</code> e recarregue.</p></html>")


def _spa_router(static_dir: Path) -> APIRouter:
    router = APIRouter()
    root = static_dir.resolve()

    @router.get("/{full_path:path}", include_in_schema=False)
    def spa(full_path: str) -> Response:
        if full_path == "api" or full_path.startswith("api/"):
            raise HTTPException(status_code=404)
        candidate = (root / full_path).resolve()
        if full_path and candidate.is_file() and candidate.is_relative_to(root):
            return FileResponse(candidate)
        index = root / "index.html"
        return FileResponse(index) if index.is_file() else HTMLResponse(MISSING_BUILD, status_code=503)

    return router


def create_app(container: Container | None = None, static_dir: Path = STATIC_DIR) -> FastAPI:
    """Cria o app com o container injetado (testes) ou montado do ambiente na inicialização."""

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        if app.state.container is None:
            app.state.container = build_container()
        yield

    app = FastAPI(title="Mesa de Alocação", version="0.1.0", docs_url="/api/docs", openapi_url="/api/openapi.json",
                  lifespan=lifespan)
    app.state.container = container
    register_error_handlers(app)
    for module in (summary, catalog, exceptions, assistants):
        app.include_router(module.router, prefix="/api")
    app.include_router(_spa_router(static_dir))
    return app


app = create_app()
