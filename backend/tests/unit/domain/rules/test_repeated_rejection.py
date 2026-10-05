from app.domain.model import PastDecision, Severity
from app.domain.rules.repeated_rejection import RepeatedRejectionRule
from tests.unit.domain.rules.conftest import make_context
from tests.unit.factories import make_line, make_store, make_week_data


def _history(*actions: str) -> tuple[PastDecision, ...]:
    return tuple(PastDecision(39 + i, "JGS", "CB-PT", a, "franchisee", "não vende aqui") for i, a in enumerate(actions))


def test_gera_excecao_baixa_quando_loja_rejeita_o_mesmo_produto_repetidamente() -> None:
    data = make_week_data(stores=(make_store("JGS"),), decision_history=_history("reject", "reject"))
    [exc] = RepeatedRejectionRule().evaluate(make_context(data, [make_line("JGS")]))
    assert exc.severity is Severity.LOW
    assert any("não vende aqui" in f for f in exc.facts)


def test_nao_gera_excecao_quando_rejeicoes_abaixo_do_limite() -> None:
    data = make_week_data(stores=(make_store("JGS"),), decision_history=_history("reject", "approve"))
    assert RepeatedRejectionRule().evaluate(make_context(data)) == []
