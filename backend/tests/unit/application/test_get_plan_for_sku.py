import pytest

from app.application.use_cases.get_plan_for_sku import GetPlanForSku
from app.domain.errors import SkuNotFound
from app.domain.model import ExecutionMode
from tests.unit.fakes import plan_for
from tests.unit.scenario import small_week


def test_plano_tem_uma_linha_por_loja_com_modo_de_execucao_quando_sku_existe() -> None:
    result = GetPlanForSku(plan_for(small_week())).execute("CB-PT")
    assert result.sizes == ("M", "G")
    modes = {row.store_id: row.execution_mode for row in result.rows}
    assert modes == {"JOI": ExecutionMode.SHIP, "BRQ": ExecutionMode.ORDER_SUGGESTION,
                     "GAS": ExecutionMode.ORDER_SUGGESTION}


def test_movimento_total_soma_envio_e_transferencias_quando_calculado() -> None:
    result = GetPlanForSku(plan_for(small_week())).execute("CB-PT")
    for row in result.rows:
        assert row.total_movement == sum(c.dc_allocated + c.transfer_in - c.transfer_out for c in row.cells)
    brq = next(r for r in result.rows if r.store_id == "BRQ")
    assert brq.total_movement < 0


def test_falha_quando_sku_nao_existe() -> None:
    with pytest.raises(SkuNotFound):
        GetPlanForSku(plan_for(small_week())).execute("XX-YY")
