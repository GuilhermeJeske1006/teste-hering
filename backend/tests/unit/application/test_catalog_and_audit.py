from app.application.use_cases.catalog import ListPolicies, ListSignals, ListSkus, ListStores, ListTransfers
from app.application.use_cases.get_audit_log import GetAuditLog
from app.domain.model import AuditEvent
from tests.unit.fakes import FakeAudit, FixedClock, plan_for
from tests.unit.scenario import small_week


def test_lista_lojas_e_produtos_do_plano_quando_consultado() -> None:
    plan = plan_for(small_week())
    assert [s.id for s in ListStores(plan).execute()] == ["JOI", "BRQ", "GAS"]
    assert [k.id for k in ListSkus(plan).execute()] == ["CB-PT", "JJ-AZ"]


def test_lista_transferencias_e_sinais_quando_consultado() -> None:
    plan = plan_for(small_week())
    assert ListTransfers(plan).execute() == list(plan.current().transfers)
    assert [s.id for s in ListSignals(plan).execute()] == ["sig-1"]


def test_lista_politicas_com_rotulo_e_valor_quando_consultado() -> None:
    policies = {p.key: p for p in ListPolicies(plan_for(small_week())).execute()}
    assert policies["signal_max_auto_adjust_pct"].value == 20.0
    assert policies["signal_max_auto_adjust_pct"].unit == "%"
    assert policies["forecast_weights"].value == [0.4, 0.3, 0.2, 0.1]


def test_registro_vem_do_mais_novo_para_o_mais_antigo_quando_limitado() -> None:
    audit = FakeAudit()
    for i in range(3):
        audit.append(AuditEvent(FixedClock().now(), "planner", "approve", f"e{i}"))
    assert [e.subject for e in GetAuditLog(audit).execute(limit=2)] == ["e2", "e1"]
