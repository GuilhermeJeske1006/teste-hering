from app.domain.model import SalesRecord, Severity
from app.domain.rules.size_curve_deviation import SizeCurveDeviationRule
from tests.unit.domain.rules.conftest import make_context
from tests.unit.factories import TOPS, make_line, make_sku, make_week_data


def _run(shares: dict[str, int], launch: int | None = None):  # type: ignore[no-untyped-def]
    sales = tuple(SalesRecord("JOI", "CB-PT", size, 40, qty) for size, qty in shares.items())
    data = make_week_data(skus=(make_sku(launch_week=launch),), sales=sales)
    lines = [make_line("JOI", size=s) for s in TOPS]
    return SizeCurveDeviationRule().evaluate(make_context(data, lines))


def test_gera_excecao_quando_dois_tamanhos_desviam_da_curva() -> None:
    [exc] = _run({"PP": 0, "P": 50, "M": 33, "G": 10, "GG": 7})
    assert exc.severity is Severity.MEDIUM
    assert len(exc.facts) == 2
    assert exc.line_keys == {("JOI", "CB-PT", s) for s in TOPS}


def test_nao_gera_excecao_quando_curva_segue_o_padrao() -> None:
    assert _run({"PP": 8, "P": 22, "M": 33, "G": 24, "GG": 13}) == []


def test_nao_gera_excecao_quando_volume_e_baixo() -> None:
    assert _run({"P": 20}) == []


def test_ignora_lancamentos_quando_avalia_curva() -> None:
    assert _run({"PP": 0, "P": 50, "M": 33, "G": 10, "GG": 7}, launch=41) == []
