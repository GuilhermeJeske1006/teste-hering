"""Motor de alocação: compõe previsão, cálculo, rateio, transferências e regras."""
from app.domain.engine import AllocationEngine
from app.domain.model import (
    AllocationException,
    DcStock,
    LineStatus,
    Ownership,
    SalesRecord,
    Severity,
    StockRecord,
)
from app.domain.rules import RuleContext, default_rules
from tests.unit.factories import make_store, make_week_data


def _data():  # type: ignore[no-untyped-def]
    stores = (make_store("JOI"), make_store("BRQ", Ownership.FRANCHISE))
    sales = tuple(SalesRecord(s, "CB-PT", "M", w, q) for s, q in (("JOI", 10), ("BRQ", 1)) for w in range(33, 41))
    stock = (StockRecord("JOI", "CB-PT", "M", 0), StockRecord("BRQ", "CB-PT", "M", 40),
             StockRecord("JOI", "CB-PT", "P", -1))
    return make_week_data(stores=stores, sales=sales, stock=stock, dc_stock=(DcStock("CB-PT", "M", 5),))


def test_gera_uma_linha_por_registro_de_estoque_ordenada_quando_roda() -> None:
    plan = AllocationEngine(default_rules()).run(_data())
    assert [line.key for line in plan.lines] == [("BRQ", "CB-PT", "M"), ("JOI", "CB-PT", "M"), ("JOI", "CB-PT", "P")]


def test_rateia_cd_e_transfere_o_que_falta_quando_cd_nao_cobre() -> None:
    plan = AllocationEngine(default_rules()).run(_data())
    joi = next(line for line in plan.lines if line.key == ("JOI", "CB-PT", "M"))
    assert joi.need == 25 and joi.dc_allocated == 5
    assert [(t.source, t.destination) for t in plan.transfers] == [("BRQ", "JOI")]
    assert joi.transfer_in == plan.transfers[0].qty


def test_bloqueia_e_gera_excecao_quando_estoque_negativo() -> None:
    plan = AllocationEngine(default_rules()).run(_data())
    blocked = [line for line in plan.lines if line.status is LineStatus.BLOCKED]
    assert [line.key for line in blocked] == [("JOI", "CB-PT", "P")]
    assert "negative_stock" in [e.rule for e in plan.exceptions]


def test_produto_sem_estoque_no_cd_recebe_zero_quando_nao_ha_registro_de_cd() -> None:
    data = make_week_data(stock=(StockRecord("JOI", "CB-PT", "G", 0),),
                          sales=tuple(SalesRecord("JOI", "CB-PT", "G", 40, 5) for _ in range(1)))
    plan = AllocationEngine([]).run(data)
    assert plan.lines[0].need > 0 and plan.lines[0].dc_allocated == 0
