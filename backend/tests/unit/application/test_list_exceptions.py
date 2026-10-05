from app.application.use_cases.list_exceptions import ListExceptions
from app.domain.model import Decision, DecisionAction, ExceptionStatus
from tests.unit.fakes import FakeDecisions, FixedClock, plan_for
from tests.unit.scenario import small_week


def test_lista_em_ordem_de_severidade_quando_sem_filtro() -> None:
    result = ListExceptions(plan_for(small_week()), FakeDecisions()).execute()
    ranks = [e.severity.rank for e in result]
    assert ranks == sorted(ranks)
    assert {e.rule for e in result} >= {"stockout_transfer", "signal_divergence", "negative_stock",
                                         "repeated_rejection"}


def test_mostra_status_e_decisao_quando_ja_decidida() -> None:
    plan, decisions = plan_for(small_week()), FakeDecisions()
    target = plan.current().exceptions[0]
    decisions.save(target.id, Decision(DecisionAction.REJECT, "planner", FixedClock().now(), "Dado de entrada errado"))
    result = {e.id: e for e in ListExceptions(plan, decisions).execute()}
    assert result[target.id].status is ExceptionStatus.REJECTED
    assert result[target.id].decision is not None and result[target.id].decision.reason == "Dado de entrada errado"


def test_filtra_por_status_quando_pedido() -> None:
    plan, decisions = plan_for(small_week()), FakeDecisions()
    target = plan.current().exceptions[0]
    decisions.save(target.id, Decision(DecisionAction.APPROVE, "planner", FixedClock().now()))
    approved = ListExceptions(plan, decisions).execute(ExceptionStatus.APPROVED)
    assert [e.id for e in approved] == [target.id]
    assert target.id not in [e.id for e in ListExceptions(plan, decisions).execute(ExceptionStatus.OPEN)]
