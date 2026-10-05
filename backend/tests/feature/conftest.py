"""Fixtures dos testes de feature: monolito completo com seed real e banco temporário."""
from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.container import build_container
from app.main import create_app


@pytest.fixture
def static_dir(tmp_path: Path) -> Path:
    static = tmp_path / "static"
    (static / "assets").mkdir(parents=True)
    (static / "index.html").write_text("<!doctype html><title>Mesa de Alocação</title><div id=root></div>")
    (static / "assets" / "app.js").write_text("console.log('ok')")
    (static / "favicon.svg").write_text("<svg xmlns='http://www.w3.org/2000/svg'/>")
    return static


@pytest.fixture
def client(tmp_path: Path, static_dir: Path) -> Iterator[TestClient]:
    container = build_container({"MESA_DB_PATH": str(tmp_path / "mesa.db")})
    with TestClient(create_app(container, static_dir=static_dir)) as c:
        yield c


def open_exceptions(client: TestClient) -> list[dict[str, object]]:
    return client.get("/api/exceptions", params={"status": "open"}).json()  # type: ignore[no-any-return]
