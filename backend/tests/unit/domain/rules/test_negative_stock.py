from app.domain.model import LineStatus, Severity
from app.domain.rules.negative_stock import NegativeStockRule
from tests.unit.domain.rules.conftest import make_context
from tests.unit.factories import make_line, make_store, make_week_data


def test_gera_uma_excecao_por_linha_bloqueada_quando_estoque_negativo() -> None:
    data = make_week_data(stores=(make_store("GAS"),))
    lines = [make_line("GAS", size="P", stock=-2, status=LineStatus.BLOCKED), make_line("GAS", size="M", stock=3)]
    [exc] = NegativeStockRule().evaluate(make_context(data, lines))
    assert exc.severity is Severity.MEDIUM
    assert exc.line_keys == {("GAS", "CB-PT", "P")}


def test_nao_gera_excecao_quando_nenhuma_linha_bloqueada() -> None:
    assert NegativeStockRule().evaluate(make_context(make_week_data(), [make_line()])) == []
