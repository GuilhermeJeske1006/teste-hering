from app.application.use_cases.generate_plan import GeneratePlan
from app.domain.engine import AllocationEngine
from app.domain.rules import default_rules
from tests.unit.fakes import FakeAudit, FakePlanStore, FakeSeed, FixedClock
from tests.unit.scenario import small_week


def test_calcula_e_guarda_o_plano_quando_executado() -> None:
    store, audit = FakePlanStore(), FakeAudit()
    plan = GeneratePlan(FakeSeed(small_week()), AllocationEngine(default_rules()), store, audit, FixedClock()).execute()
    assert store.plan is plan
    assert len(plan.lines) == 8


def test_registra_a_recomendacao_na_auditoria_quando_executado() -> None:
    audit = FakeAudit()
    GeneratePlan(FakeSeed(small_week()), AllocationEngine(default_rules()), FakePlanStore(), audit,
                 FixedClock()).execute()
    [event] = audit.events
    assert event.actor == "sistema" and event.action == "recommend"
    assert "8 linhas" in (event.detail or "")
