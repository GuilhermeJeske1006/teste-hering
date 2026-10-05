"""Alvo, necessidade e excesso (regras.md §4)."""
from app.domain.allocation import LineCalculator
from app.domain.forecasting import Forecast
from app.domain.model import LineStatus
from tests.unit.factories import make_policies, make_sku


def _calc(stock: int, horizon: float, *, basic: bool = True, weekly: float = 1.0):  # type: ignore[no-untyped-def]
    return LineCalculator(make_policies()).calculate(
        "JOI", make_sku(is_basic=basic), "M", stock, Forecast(weekly, horizon))


def test_linha_fica_bloqueada_com_alvo_zero_quando_estoque_negativo() -> None:
    line = _calc(-2, 10.0)
    assert line.status is LineStatus.BLOCKED
    assert (line.target, line.need, line.excess) == (0, 0, 0)


def test_alvo_e_previsao_vezes_cobertura_arredondada_para_cima_quando_maior_que_exposicao() -> None:
    line = _calc(2, 8.4)
    assert line.target == 11  # ceil(8.4 * 1.25) = ceil(10.5)
    assert line.need == 9


def test_alvo_usa_exposicao_minima_de_basico_quando_previsao_baixa() -> None:
    assert _calc(0, 0.4).target == 3


def test_alvo_usa_exposicao_minima_de_nao_basico_quando_previsao_baixa() -> None:
    assert _calc(0, 0.4, basic=False).target == 1


def test_excesso_libera_acima_de_previsao_vezes_fator_quando_estoque_passa_do_gatilho() -> None:
    line = _calc(40, 4.0)
    assert line.need == 0
    assert line.excess == 34  # floor(40 - 4.0 * 1.5)


def test_sem_necessidade_nem_excesso_quando_estoque_entre_alvo_e_gatilho() -> None:
    line = _calc(8, 4.0)
    assert (line.need, line.excess) == (0, 0)


def test_linha_guarda_previsoes_quando_calculada() -> None:
    line = _calc(2, 8.4, weekly=4.2)
    assert (line.weekly_forecast, line.forecast_horizon) == (4.2, 8.4)
