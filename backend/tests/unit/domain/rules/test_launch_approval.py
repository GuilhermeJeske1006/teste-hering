from app.domain.model import Severity
from app.domain.rules.launch_approval import LaunchApprovalRule
from tests.unit.domain.rules.conftest import make_context
from tests.unit.factories import make_line, make_sku, make_store, make_week_data


def _data(launch_week: int):  # type: ignore[no-untyped-def]
    sku = make_sku("VM-FL", launch_week=launch_week, similar=("R1",), is_basic=False)
    return make_week_data(stores=(make_store("JOI"), make_store("BC")), skus=(sku, make_sku("CB-PT")))


def test_gera_excecao_critica_com_necessidade_por_loja_quando_lancamento_recente() -> None:
    lines = [make_line("JOI", "VM-FL", "M", target=4, need=4), make_line("JOI", "VM-FL", "G", target=2, need=2),
             make_line("BC", "VM-FL", "M", target=3, need=3), make_line("BC", "CB-PT", "M", target=9, need=9)]
    [exc] = LaunchApprovalRule().evaluate(make_context(_data(41), lines))
    assert exc.rule == "launch_approval" and exc.severity is Severity.CRITICAL
    assert "9 peças em 2 lojas" in exc.recommendation
    assert exc.line_keys == {("JOI", "VM-FL", "M"), ("JOI", "VM-FL", "G"), ("BC", "VM-FL", "M")}


def test_nao_gera_excecao_quando_lancamento_ja_passou_da_janela() -> None:
    assert LaunchApprovalRule().evaluate(make_context(_data(39))) == []
