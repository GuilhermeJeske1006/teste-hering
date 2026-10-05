from dataclasses import replace

from app.application.use_cases.get_summary import GetSummary
from app.domain.model import Decision, DecisionAction
from tests.unit.fakes import FakeDecisions, FixedClock, plan_for
from tests.unit.scenario import small_week


def test_resumo_conta_linhas_excecoes_e_transferencias_quando_nada_foi_decidido() -> None:
    plan = plan_for(small_week())
    summary = GetSummary(plan, FakeDecisions()).execute()
    assert summary.total_lines == 8
    assert summary.open_exceptions == len(plan.current().exceptions)
    assert summary.transfers == len(plan.current().transfers)
    assert summary.shadow_mode is True
    assert summary.week.iso_week == 41


def test_linhas_dentro_da_politica_excluem_bloqueadas_e_referenciadas_quando_ha_excecoes_abertas() -> None:
    plan = plan_for(small_week())
    referenced = set().union(*(e.line_keys for e in plan.current().exceptions))
    blocked = {line.key for line in plan.current().lines if line.status.value == "blocked"}
    expected = sum(1 for line in plan.current().lines if line.key not in referenced | blocked)
    assert GetSummary(plan, FakeDecisions()).execute().within_policy == expected


def test_aprovar_aumenta_linhas_dentro_da_politica_quando_excecao_sai_da_fila() -> None:
    plan, decisions = plan_for(small_week()), FakeDecisions()
    before = GetSummary(plan, decisions).execute()
    others = [e for e in plan.current().exceptions]
    target = next(e for e in others if ("JOI", "CB-PT", "G") in e.line_keys)
    assert all(("JOI", "CB-PT", "G") not in e.line_keys for e in others if e is not target)
    decisions.save(target.id, Decision(DecisionAction.APPROVE, "planner", FixedClock().now()))
    after = GetSummary(plan, decisions).execute()
    assert after.open_exceptions == before.open_exceptions - 1
    assert after.within_policy > before.within_policy
    assert replace(after, within_policy=0, open_exceptions=0) == replace(before, within_policy=0, open_exceptions=0)
