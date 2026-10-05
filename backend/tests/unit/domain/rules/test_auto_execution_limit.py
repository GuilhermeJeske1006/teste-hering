from app.domain.model import Ownership, Severity
from app.domain.rules.auto_execution_limit import AutoExecutionLimitRule
from tests.unit.domain.rules.conftest import make_context
from tests.unit.factories import make_line, make_policies, make_sku, make_store, make_week_data


def _data(limit: float):  # type: ignore[no-untyped-def]
    return make_week_data(stores=(make_store("JOI"), make_store("BRQ", Ownership.FRANCHISE)),
                          skus=(make_sku(price=100.0), make_sku("VM-FL", price=100.0, launch_week=41)),
                          policies=make_policies(auto_execution_max_value_brl=limit))


LINES = [make_line("JOI", target=10, need=10, dc_allocated=10), make_line("BRQ", target=50, need=50, dc_allocated=50),
         make_line("JOI", "VM-FL", target=90, need=90, dc_allocated=90)]


def test_gera_excecao_quando_envio_de_loja_propria_passa_do_limite() -> None:
    [exc] = AutoExecutionLimitRule().evaluate(make_context(_data(500.0), LINES))
    assert exc.severity is Severity.MEDIUM
    assert "R$ 1.000,00" in exc.recommendation
    assert exc.line_keys == {("JOI", "CB-PT", "M")}


def test_nao_gera_excecao_quando_envio_fica_dentro_do_limite_sem_lancamentos() -> None:
    assert AutoExecutionLimitRule().evaluate(make_context(_data(1000.0), LINES)) == []
