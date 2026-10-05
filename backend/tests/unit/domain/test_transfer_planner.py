"""Transferências entre lojas quando o CD não cobre (regras.md §6)."""
from app.domain.allocation import TransferPlanner
from app.domain.model import Transfer
from tests.unit.factories import make_line, make_policies


def _dest(store: str, *, stock: int, need: int, dc: int, weekly: float, horizon: float):  # type: ignore[no-untyped-def]
    return make_line(store, stock=stock, weekly=weekly, horizon=horizon, target=stock + need, need=need,
                     dc_allocated=dc)


def _source(store: str, *, stock: int, excess: int, weekly: float):  # type: ignore[no-untyped-def]
    return make_line(store, stock=stock, weekly=weekly, horizon=weekly * 2, target=3, excess=excess)


def test_transfere_do_maior_excesso_para_maior_venda_perdida_quando_cd_nao_cobre() -> None:
    lines = [
        _dest("JOI", stock=1, need=15, dc=2, weekly=6.0, horizon=12.0),
        _dest("BC", stock=2, need=5, dc=1, weekly=3.0, horizon=6.0),
        _source("BRQ", stock=40, excess=10, weekly=2.0),
    ]
    updated, transfers = TransferPlanner(make_policies()).plan(lines)
    assert transfers == [Transfer("CB-PT", "M", "BRQ", "JOI", 10)]
    by_store = {ln.store: ln for ln in updated}
    assert by_store["BRQ"].transfer_out == 10
    assert by_store["JOI"].transfer_in == 10
    assert by_store["BC"].transfer_in == 0


def test_destino_nao_recebe_quando_cobertura_apos_cd_ja_atinge_horizonte() -> None:
    lines = [_dest("JOI", stock=10, need=3, dc=0, weekly=4.0, horizon=8.0),
             _source("BRQ", stock=40, excess=10, weekly=2.0)]
    _, transfers = TransferPlanner(make_policies()).plan(lines)
    assert transfers == []


def test_origem_nao_cede_quando_cobertura_propria_e_baixa() -> None:
    lines = [_dest("JOI", stock=0, need=5, dc=0, weekly=4.0, horizon=8.0),
             _source("BRQ", stock=40, excess=10, weekly=10.0)]
    _, transfers = TransferPlanner(make_policies()).plan(lines)
    assert transfers == []


def test_destino_completa_com_varias_origens_quando_uma_nao_basta() -> None:
    lines = [_dest("JOI", stock=0, need=12, dc=0, weekly=6.0, horizon=12.0),
             _source("BRQ", stock=40, excess=8, weekly=2.0),
             _source("ITJ", stock=40, excess=8, weekly=2.0)]
    _, transfers = TransferPlanner(make_policies()).plan(lines)
    assert transfers == [Transfer("CB-PT", "M", "BRQ", "JOI", 8), Transfer("CB-PT", "M", "ITJ", "JOI", 4)]


def test_linha_sem_previsao_nao_recebe_quando_cobertura_e_infinita() -> None:
    lines = [_dest("JOI", stock=0, need=3, dc=0, weekly=0.0, horizon=0.0),
             _source("BRQ", stock=40, excess=10, weekly=2.0)]
    _, transfers = TransferPlanner(make_policies()).plan(lines)
    assert transfers == []
