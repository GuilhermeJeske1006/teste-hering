"""Leitura do seed JSON para objetos de domínio."""
import json
from pathlib import Path

import pytest

from app.domain.model import ExecutionMode, SignalType
from app.infrastructure.seed_json import JsonSeedSource, SeedFormatError

SEED = Path(__file__).resolve().parents[3] / "app" / "seed" / "seed.json"


def test_carrega_semana_lojas_produtos_e_estoque_quando_le_o_seed_real() -> None:
    data = JsonSeedSource(SEED).load()
    assert data.week.iso_week == 41 and str(data.week.start) == "2026-10-05"
    assert len(data.stores) == 8 and len(data.skus) == 6 and len(data.stock) == 248
    assert data.store("JOI") is not None and data.store("JOI").execution_mode is ExecutionMode.SHIP  # type: ignore[union-attr]
    vm = data.sku("VM-FL")
    assert vm is not None and vm.is_launch and vm.sizes == ("PP", "P", "M", "G", "GG")
    assert data.signals[0].type is SignalType.LOCAL_EVENT and data.signals[0].adjustments[0].pct == 40
    assert data.policies.forecast_weights == (0.4, 0.3, 0.2, 0.1)


def test_falha_com_mensagem_clara_quando_produto_usa_grade_inexistente(tmp_path: Path) -> None:
    raw = json.loads(SEED.read_text())
    raw["skus"][0]["size_grid"] = "inexistente"
    path = tmp_path / "seed.json"
    path.write_text(json.dumps(raw))
    with pytest.raises(SeedFormatError, match="grade"):
        JsonSeedSource(path).load()


def test_falha_com_mensagem_clara_quando_estoque_cita_loja_inexistente(tmp_path: Path) -> None:
    raw = json.loads(SEED.read_text())
    raw["stock"][0]["store"] = "XXX"
    path = tmp_path / "seed.json"
    path.write_text(json.dumps(raw))
    with pytest.raises(SeedFormatError, match="XXX"):
        JsonSeedSource(path).load()
