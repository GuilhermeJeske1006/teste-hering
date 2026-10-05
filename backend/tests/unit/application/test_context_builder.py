from app.application.context_builder import ContextBuilder
from app.domain.model import Decision, DecisionAction
from tests.unit.fakes import FakeDecisions, FixedClock, plan_for
from tests.unit.scenario import small_week


def test_contexto_traz_politicas_excecoes_com_status_e_sinais_quando_construido() -> None:
    plan, decisions = plan_for(small_week()), FakeDecisions()
    first = plan.current().exceptions[0]
    decisions.save(first.id, Decision(DecisionAction.APPROVE, "planejador", FixedClock().now()))
    ctx = ContextBuilder(plan, decisions).build()
    assert ctx.text.startswith("<contexto>") and ctx.text.rstrip().endswith("</contexto>")
    assert "Ajuste automático máximo por sinal: 20" in ctx.text
    assert f"[{first.id}]" in ctx.text and "aprovada" in ctx.text
    assert "sig-1" in ctx.text
    assert set(ctx.exception_ids) == {e.id for e in plan.current().exceptions}


def test_contexto_inclui_plano_do_produto_em_foco_quando_informado() -> None:
    ctx = ContextBuilder(plan_for(small_week()), FakeDecisions()).build("CB-PT")
    assert "Plano de CB-PT" in ctx.text
    assert "JOI (envio)" in ctx.text and "BRQ (sugestão de pedido)" in ctx.text


def test_contexto_ignora_foco_quando_produto_nao_existe() -> None:
    ctx = ContextBuilder(plan_for(small_week()), FakeDecisions()).build("XX")
    assert "Plano de" not in ctx.text
