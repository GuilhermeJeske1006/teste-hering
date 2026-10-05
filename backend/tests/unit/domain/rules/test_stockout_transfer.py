from app.domain.model import DcStock, Ownership, Severity, Transfer
from app.domain.rules.stockout_transfer import StockoutTransferRule
from tests.unit.domain.rules.conftest import make_context
from tests.unit.factories import make_line, make_store, make_week_data


def test_agrupa_destinos_por_produto_tamanho_e_origem_quando_ha_transferencias() -> None:
    data = make_week_data(stores=(make_store("BRQ", Ownership.FRANCHISE), make_store("JOI"), make_store("BC")),
                          dc_stock=(DcStock("CB-PT", "M", 5),))
    lines = [make_line("BRQ", stock=40, weekly=2.0, target=3, excess=30, transfer_out=14),
             make_line("JOI", target=12, need=12, dc_allocated=3, transfer_in=9),
             make_line("BC", target=8, need=8, dc_allocated=2, transfer_in=5)]
    transfers = [Transfer("CB-PT", "M", "BRQ", "JOI", 9), Transfer("CB-PT", "M", "BRQ", "BC", 5)]
    [exc] = StockoutTransferRule().evaluate(make_context(data, lines, transfers))
    assert exc.severity is Severity.HIGH
    assert exc.recommendation == "Transferir 14 peças de BRQ: 9 para JOI e 5 para BC"
    assert ("BRQ", "CB-PT", "M") in exc.line_keys and ("BC", "CB-PT", "M") in exc.line_keys


def test_nao_gera_excecao_quando_nao_ha_transferencias() -> None:
    assert StockoutTransferRule().evaluate(make_context(make_week_data())) == []
