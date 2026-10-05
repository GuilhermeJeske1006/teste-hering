from app.domain.model import SalesRecord, Severity
from app.domain.rules.seasonal_decline import SeasonalDeclineRule
from tests.unit.domain.rules.conftest import make_context
from tests.unit.factories import make_line, make_policies, make_sku, make_store, make_week_data

STORES = ("A", "B", "C")


def _sales(store: str, before: int, after: int) -> tuple[SalesRecord, ...]:
    weeks = [(w, before) for w in (35, 36, 37)] + [(w, after) for w in (38, 39, 40)]
    return tuple(SalesRecord(store, "MC-CZ", "M", w, q) for w, q in weeks)


def _run(stores: tuple[str, ...], after: int, stock: int, launch: int | None = None):  # type: ignore[no-untyped-def]
    sku = make_sku("MC-CZ", is_basic=False, sizes=("M",), launch_week=launch)
    data = make_week_data(stores=tuple(make_store(s) for s in stores), skus=(sku,),
                          sales=tuple(r for s in stores for r in _sales(s, 10, after)),
                          policies=make_policies())
    lines = [make_line(s, "MC-CZ", "M", stock=stock, weekly=1.0, target=1) for s in stores]
    return SeasonalDeclineRule().evaluate(make_context(data, lines))


def test_gera_excecao_quando_queda_e_cobertura_alta_em_lojas_suficientes() -> None:
    [exc] = _run(STORES, after=5, stock=10)
    assert exc.severity is Severity.MEDIUM
    assert len(exc.line_keys) == 3


def test_nao_gera_excecao_quando_poucas_lojas_caem() -> None:
    assert _run(("A", "B"), after=5, stock=10) == []


def test_nao_gera_excecao_quando_cobertura_e_baixa() -> None:
    assert _run(STORES, after=5, stock=2) == []


def test_nao_gera_excecao_quando_queda_e_pequena() -> None:
    assert _run(STORES, after=9, stock=10) == []


def test_ignora_lancamentos_quando_avalia_queda() -> None:
    assert _run(STORES, after=5, stock=10, launch=41) == []
