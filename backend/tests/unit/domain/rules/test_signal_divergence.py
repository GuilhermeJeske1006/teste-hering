from app.domain.model import Severity, SignalAdjustment
from app.domain.rules.signal_divergence import SignalDivergenceRule
from tests.unit.domain.rules.conftest import make_context
from tests.unit.factories import make_line, make_signal, make_week_data


def test_gera_uma_excecao_por_ajuste_acima_do_limite_quando_sinal_pede_demais() -> None:
    signal = make_signal("sig-1", "JOI", (SignalAdjustment("all", 40), SignalAdjustment("CB-PT:M", 10)))
    data = make_week_data(signals=(signal,))
    lines = [make_line("JOI", size="M"), make_line("JOI", size="G"), make_line("BC", size="M")]
    [exc] = SignalDivergenceRule().evaluate(make_context(data, lines))
    assert exc.severity is Severity.HIGH
    assert exc.line_keys == {("JOI", "CB-PT", "M"), ("JOI", "CB-PT", "G")}


def test_nao_gera_excecao_quando_ajuste_esta_no_limite() -> None:
    data = make_week_data(signals=(make_signal(adjustments=(SignalAdjustment("all", 20),)),))
    assert SignalDivergenceRule().evaluate(make_context(data)) == []
