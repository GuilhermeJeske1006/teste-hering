"""Golden da semana 41: o motor com o seed real reproduz expected_week41.json (skill dominio-alocacao)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.domain.engine import AllocationEngine
from app.domain.model import AllocationPlan
from app.domain.rules import default_rules
from app.infrastructure.seed_json import JsonSeedSource

ROOT = Path(__file__).resolve().parents[3]
SEED = ROOT / "backend" / "app" / "seed" / "seed.json"
EXPECTED = ROOT / ".claude" / "skills" / "dominio-alocacao" / "references" / "expected_week41.json"
EXACT_FIELDS = ("target", "need", "excess", "dc_allocated", "transfer_in", "transfer_out")


@pytest.fixture(scope="module")
def plan() -> AllocationPlan:
    return AllocationEngine(default_rules()).run(JsonSeedSource(SEED).load())


@pytest.fixture(scope="module")
def expected() -> dict[str, object]:
    return json.loads(EXPECTED.read_text())  # type: ignore[no-any-return]


def test_motor_gera_248_linhas_quando_roda_o_seed_da_semana_41(plan: AllocationPlan) -> None:
    assert len(plan.lines) == 248


def test_linhas_batem_com_o_golden_quando_comparadas_campo_a_campo(plan: AllocationPlan, expected: dict) -> None:  # type: ignore[type-arg]
    golden = {(e["store"], e["sku"], e["size"]): e for e in expected["lines"]}
    diffs = []
    for line in plan.lines:
        exp = golden[line.key]
        diffs += [(line.key, f, getattr(line, f), exp[f]) for f in EXACT_FIELDS if getattr(line, f) != exp[f]]
        if line.status.value != exp["status"]:
            diffs.append((line.key, "status", line.status.value, exp["status"]))
        if abs(line.forecast_horizon - exp["forecast_horizon"]) > 1e-3:
            diffs.append((line.key, "forecast_horizon", line.forecast_horizon, exp["forecast_horizon"]))
    assert diffs[:5] == []
    assert set(golden) == {line.key for line in plan.lines}


def test_transferencias_batem_com_o_golden_quando_cd_nao_cobre_cb_pt_m(plan: AllocationPlan, expected: dict) -> None:  # type: ignore[type-arg]
    got = [{"sku": t.sku, "size": t.size, "source": t.source, "destination": t.destination, "qty": t.qty}
           for t in plan.transfers]
    assert got == expected["transfers"]
    assert [(t.destination, t.qty) for t in plan.transfers] == [("JOI", 13), ("BNU-S", 8), ("BC", 1)]


def test_sete_excecoes_nas_regras_esperadas_quando_motor_avalia(plan: AllocationPlan, expected: dict) -> None:  # type: ignore[type-arg]
    assert [e.rule for e in plan.exceptions] == [e["rule"] for e in expected["exceptions"]]
    assert [e.rule for e in plan.exceptions] == ["launch_approval", "stockout_transfer", "signal_divergence",
                                                 "seasonal_decline", "size_curve_deviation", "negative_stock",
                                                 "repeated_rejection"]


def test_api_expoe_o_mesmo_golden_quando_consultada(client: TestClient, expected: dict) -> None:  # type: ignore[type-arg]
    """Dado o monolito com o seed real, quando consulto a API, então vejo as transferências e exceções do golden."""
    assert client.get("/api/transfers").json() == expected["transfers"]
    rules = sorted(e["rule"] for e in client.get("/api/exceptions").json())
    assert rules == sorted(e["rule"] for e in expected["exceptions"])  # type: ignore[union-attr]
