"""Aberto/fechado: uma regra nova entra no resultado sem mudar o motor (ADR 0005)."""
from app.domain.engine import AllocationEngine
from app.domain.model import AllocationException, Severity
from app.domain.rules import RuleContext, default_rules
from tests.unit.factories import make_week_data


class AlwaysFlagRule:
    """Regra fake: sempre gera uma exceção baixa."""

    rule = "fake_rule"
    severity = Severity.LOW

    def evaluate(self, ctx: RuleContext) -> list[AllocationException]:
        return [AllocationException("fake-1", self.rule, self.severity, "Regra fake", "Nada", "Teste", ("1",))]


def test_regra_fake_aparece_no_resultado_quando_injetada_no_motor() -> None:
    plan = AllocationEngine([*default_rules(), AlwaysFlagRule()]).run(make_week_data())
    assert plan.exceptions[-1].rule == "fake_rule"


def test_motor_sem_regras_nao_gera_excecoes_quando_lista_vazia() -> None:
    assert AllocationEngine([]).run(make_week_data()).exceptions == ()
