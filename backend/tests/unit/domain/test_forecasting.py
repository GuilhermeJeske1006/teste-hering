"""Previsão semanal e do horizonte (regras.md §2–3)."""
from app.domain.forecasting import (
    EventUplift,
    Forecast,
    LaunchAwareForecaster,
    SalesIndex,
    SignalUplift,
    SimilarityLaunchForecaster,
    UpliftDecorator,
    WeightedMovingAverageForecaster,
)
from app.domain.model import Event, ReferenceSale, SalesRecord, SignalAdjustment
from tests.unit.factories import make_policies, make_signal, make_sku


def _sales(*weeks_qty: tuple[int, int], store: str = "JOI", sku: str = "CB-PT", size: str = "M") -> SalesIndex:
    return SalesIndex(tuple(SalesRecord(store, sku, size, w, q) for w, q in weeks_qty))


class FixedForecaster:
    def __init__(self, weekly: float, horizon: float) -> None:
        self._f = Forecast(weekly, horizon)

    def forecast(self, store: str, sku: object, size: str) -> Forecast:
        return self._f


def test_media_ponderada_usa_pesos_da_semana_mais_recente_quando_ha_historico() -> None:
    index = _sales((40, 10), (39, 5), (38, 2), (37, 20))
    forecaster = WeightedMovingAverageForecaster(index, current_week=41, policies=make_policies())
    result = forecaster.forecast("JOI", make_sku(), "M")
    assert result.weekly == 0.4 * 10 + 0.3 * 5 + 0.2 * 2 + 0.1 * 20
    assert result.horizon == result.weekly * 2


def test_media_ponderada_conta_zero_quando_semana_sem_registro() -> None:
    index = _sales((40, 10))
    forecaster = WeightedMovingAverageForecaster(index, current_week=41, policies=make_policies())
    assert forecaster.forecast("JOI", make_sku(), "M").weekly == 4.0


def test_lancamento_usa_media_dos_similares_dividida_por_duas_semanas_quando_ha_referencia() -> None:
    refs = (ReferenceSale("REF-1", "JOI", "M", 6), ReferenceSale("REF-2", "JOI", "M", 10),
            ReferenceSale("OUTRO", "JOI", "M", 100), ReferenceSale("REF-1", "BC", "M", 50))
    forecaster = SimilarityLaunchForecaster(refs, make_policies())
    launch = make_sku("VM-FL", launch_week=41, similar=("REF-1", "REF-2"))
    result = forecaster.forecast("JOI", launch, "M")
    assert result.weekly == 4.0
    assert result.horizon == 8.0


def test_lancamento_preve_zero_quando_nao_ha_referencia() -> None:
    forecaster = SimilarityLaunchForecaster((), make_policies())
    launch = make_sku("VM-FL", launch_week=41, similar=("REF-1",))
    assert forecaster.forecast("JOI", launch, "M") == Forecast(0.0, 0.0)


def test_roteador_escolhe_previsor_de_lancamento_quando_sku_e_lancamento() -> None:
    router = LaunchAwareForecaster(history=FixedForecaster(1, 2), launch=FixedForecaster(5, 10))
    assert router.forecast("JOI", make_sku(launch_week=41), "M").weekly == 5
    assert router.forecast("JOI", make_sku(), "M").weekly == 1


def test_uplift_de_evento_soma_categoria_quando_loja_participa_e_evento_sobrepoe_horizonte() -> None:
    events = (Event("e1", "Oktoberfest", ("JOI",), 41, 43, {"tees": 0.22}),
              Event("e2", "Passado", ("JOI",), 30, 40, {"tees": 0.5}),
              Event("e3", "Outra loja", ("BC",), 41, 41, {"tees": 0.5}))
    uplift = EventUplift(events, current_week=41, policies=make_policies())
    assert uplift.uplift("JOI", make_sku(), "M") == 0.22
    assert uplift.uplift("JOI", make_sku(category="jackets"), "M") == 0.0


def test_uplift_de_sinal_ignora_ajuste_acima_do_limite_quando_calcula() -> None:
    signals = (make_signal("s1", "JOI", (SignalAdjustment("CB-PT:M", 15), SignalAdjustment("all", 40))),
               make_signal("s2", "BC", (SignalAdjustment("all", 10),)))
    uplift = SignalUplift(signals, make_policies())
    assert uplift.uplift("JOI", make_sku(), "M") == 0.15
    assert uplift.uplift("JOI", make_sku(), "G") == 0.0


def test_decorator_aplica_soma_dos_uplifts_ao_horizonte_quando_ha_fontes() -> None:
    events = (Event("e1", "Oktoberfest", ("JOI",), 41, 43, {"tees": 0.2}),)
    signals = (make_signal("s1", "JOI", (SignalAdjustment("all", 10),)),)
    decorated = UpliftDecorator(FixedForecaster(4.0, 8.0), sources=(
        EventUplift(events, current_week=41, policies=make_policies()),
        SignalUplift(signals, make_policies()),
    ))
    result = decorated.forecast("JOI", make_sku(), "M")
    assert result.weekly == 4.0
    assert abs(result.horizon - 4.0 * 2 * 1.3) < 1e-9
