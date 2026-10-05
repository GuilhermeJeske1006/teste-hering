"""Suíte de contrato dos repositórios (Liskov): InMemory e Sqlite se comportam igual (ADR 0008)."""
from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.application.ports import AuditLog, DecisionReader, DecisionWriter
from app.domain.model import AuditEvent, Decision, DecisionAction
from app.infrastructure.memory_repos import InMemoryAuditLog, InMemoryDecisionRepository
from app.infrastructure.sqlite_repos import SqliteAuditLog, SqliteDecisionRepository

AT = datetime(2026, 10, 5, 12, 30, tzinfo=UTC)


class DecisionRepo(DecisionReader, DecisionWriter):
    """Tipo de conveniência: o repositório concreto implementa leitura e escrita."""


@pytest.fixture(params=["memory", "sqlite"])
def decisions(request: pytest.FixtureRequest, tmp_path: Path) -> Iterator[DecisionRepo]:
    yield (InMemoryDecisionRepository() if request.param == "memory"  # type: ignore[misc]
           else SqliteDecisionRepository(tmp_path / "repo.db"))


@pytest.fixture(params=["memory", "sqlite"])
def audit(request: pytest.FixtureRequest, tmp_path: Path) -> Iterator[AuditLog]:
    yield InMemoryAuditLog() if request.param == "memory" else SqliteAuditLog(tmp_path / "repo.db")


def test_devolve_none_quando_excecao_sem_decisao(decisions: DecisionRepo) -> None:
    assert decisions.get("x") is None
    assert dict(decisions.all()) == {}


def test_devolve_decisao_igual_a_gravada_quando_salva(decisions: DecisionRepo) -> None:
    decision = Decision(DecisionAction.REJECT, "planejador", AT, "Dado de entrada errado")
    decisions.save("abc", decision)
    assert decisions.get("abc") == decision
    assert dict(decisions.all()) == {"abc": decision}


def test_substitui_decisao_quando_salva_de_novo(decisions: DecisionRepo) -> None:
    decisions.save("abc", Decision(DecisionAction.APPROVE, "planejador", AT))
    decisions.save("abc", Decision(DecisionAction.REJECT, "planejador", AT, "Dado de entrada errado"))
    assert decisions.get("abc") == Decision(DecisionAction.REJECT, "planejador", AT, "Dado de entrada errado")


def test_remove_decisao_quando_desfeita(decisions: DecisionRepo) -> None:
    decisions.save("abc", Decision(DecisionAction.APPROVE, "planejador", AT))
    decisions.delete("abc")
    decisions.delete("nao-existe")
    assert decisions.get("abc") is None


def test_lista_eventos_do_mais_novo_para_o_mais_antigo_quando_le(audit: AuditLog) -> None:
    for i in range(3):
        audit.append(AuditEvent(AT, "planejador", "approve", f"e{i}", None, f"id{i}"))
    assert [e.subject for e in audit.recent(10)] == ["e2", "e1", "e0"]


def test_respeita_o_limite_quando_le_eventos(audit: AuditLog) -> None:
    for i in range(3):
        audit.append(AuditEvent(AT, "planejador", "approve", f"e{i}"))
    assert [e.subject for e in audit.recent(2)] == ["e2", "e1"]
    assert audit.recent(0) == []


def test_preserva_todos_os_campos_quando_grava_evento(audit: AuditLog) -> None:
    event = AuditEvent(AT, "planejador", "reject", "Título", "Restrição comercial com o franqueado", "abc")
    audit.append(event)
    assert audit.recent(1) == [event]
