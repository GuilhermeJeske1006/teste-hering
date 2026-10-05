"""Invariantes das entidades de domínio."""
from dataclasses import FrozenInstanceError, replace

import pytest

from app.domain.model import (
    AllocationLine,
    ExecutionMode,
    LineStatus,
    Ownership,
    Policies,
    Severity,
    SignalAdjustment,
    Sku,
    Store,
    Transfer,
)
from tests.unit.factories import make_policies


def test_policies_sao_imutaveis_quando_alguem_tenta_alterar_um_limite() -> None:
    policies = make_policies()
    with pytest.raises(FrozenInstanceError):
        policies.cover_factor = 9.9  # type: ignore[misc]


def test_policies_rejeitam_pesos_vazios_quando_construidas() -> None:
    with pytest.raises(ValueError):
        replace(make_policies(), forecast_weights=())


def test_policies_rejeitam_horizonte_zero_quando_construidas() -> None:
    with pytest.raises(ValueError):
        replace(make_policies(), horizon_weeks=0)


def test_policies_carregam_janela_sazonal_padrao_quando_omitida() -> None:
    assert make_policies().seasonal_window_weeks == 3


def test_linha_rejeita_necessidade_negativa_quando_construida() -> None:
    with pytest.raises(ValueError):
        AllocationLine("JOI", "CB-PT", "M", stock=3, weekly_forecast=1.0, forecast_horizon=2.0, need=-1)


def test_linha_rejeita_envio_maior_que_necessidade_quando_construida() -> None:
    with pytest.raises(ValueError):
        AllocationLine("JOI", "CB-PT", "M", stock=3, weekly_forecast=1.0, forecast_horizon=2.0,
                       target=5, need=2, dc_allocated=3)


def test_linha_bloqueada_exige_alvo_zero_quando_construida() -> None:
    with pytest.raises(ValueError):
        AllocationLine("GAS", "CV-BR", "P", stock=-2, weekly_forecast=1.0, forecast_horizon=2.0,
                       target=3, status=LineStatus.BLOCKED)


def test_linha_calcula_falta_e_excesso_disponivel_quando_tem_movimentos() -> None:
    line = AllocationLine("BRQ", "CB-PT", "M", stock=40, weekly_forecast=2.0, forecast_horizon=4.0,
                          target=5, excess=30, transfer_out=10)
    assert line.available_excess == 20
    assert line.key == ("BRQ", "CB-PT", "M")
    short = AllocationLine("JOI", "CB-PT", "M", stock=1, weekly_forecast=2.0, forecast_horizon=4.0,
                           target=5, need=4, dc_allocated=1)
    assert short.short == 3


def test_loja_propria_recebe_envio_quando_ownership_e_own() -> None:
    assert Store("JOI", "Joinville", Ownership.OWN, "Vale").execution_mode is ExecutionMode.SHIP


def test_franquia_recebe_sugestao_de_pedido_quando_ownership_e_franchise() -> None:
    store = Store("BRQ", "Brusque", Ownership.FRANCHISE, "Vale")
    assert store.execution_mode is ExecutionMode.ORDER_SUGGESTION


def test_sku_e_lancamento_quando_tem_semana_de_lancamento() -> None:
    launch = Sku("VM-FL", "Vestido", "dresses", "tops", ("P",), 229.9, False, launch_week=41)
    basic = Sku("CB-PT", "Camiseta", "tees", "tops", ("P",), 59.9, True)
    assert launch.is_launch and not basic.is_launch


def test_ajuste_de_sinal_vale_para_escopo_compativel_quando_comparado() -> None:
    assert SignalAdjustment("all", 10).applies_to("CB-PT", "M")
    assert SignalAdjustment("CB-PT", 10).applies_to("CB-PT", "M")
    assert SignalAdjustment("CB-PT:M", 10).applies_to("CB-PT", "M")
    assert not SignalAdjustment("CB-PT:G", 10).applies_to("CB-PT", "M")


def test_transferencia_rejeita_quantidade_zero_quando_construida() -> None:
    with pytest.raises(ValueError):
        Transfer("CB-PT", "M", "BRQ", "JOI", 0)


def test_severidade_ordena_da_critica_para_a_baixa_quando_comparada() -> None:
    ranks = [s.rank for s in (Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW)]
    assert ranks == sorted(ranks)
