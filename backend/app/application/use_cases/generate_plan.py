"""Caso de uso: recalcular o plano da semana a partir dos dados de entrada."""
from __future__ import annotations

from app.application.ports import AuditLog, Clock, PlanWriter, SeedSource
from app.domain.engine import AllocationEngine
from app.domain.model import AllocationPlan, AuditEvent

SYSTEM_ACTOR = "sistema"


class GeneratePlan:
    """Roda o motor, guarda o plano e registra a recomendação na auditoria."""

    def __init__(self, seed: SeedSource, engine: AllocationEngine, writer: PlanWriter, audit: AuditLog,
                 clock: Clock) -> None:
        self._seed, self._engine, self._writer, self._audit, self._clock = seed, engine, writer, audit, clock

    def execute(self) -> AllocationPlan:
        plan = self._engine.run(self._seed.load())
        self._writer.save(plan)
        week = plan.data.week
        self._audit.append(AuditEvent(
            timestamp=self._clock.now(), actor=SYSTEM_ACTOR, action="recommend",
            subject=f"Plano da semana {week.iso_week}/{week.year}",
            detail=f"{len(plan.lines)} linhas, {len(plan.transfers)} transferências e "
                   f"{len(plan.exceptions)} exceções",
        ))
        return plan
