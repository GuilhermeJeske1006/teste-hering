"""Rotas de saúde e resumo da semana."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_container
from app.api.schemas import HealthOut, SummaryOut, WeekOut
from app.container import Container

router = APIRouter()
Deps = Annotated[Container, Depends(get_container)]


@router.get("/health", response_model=HealthOut)
def health(c: Deps) -> HealthOut:
    return HealthOut(llm=c.llm_name)  # type: ignore[arg-type]


@router.get("/summary", response_model=SummaryOut)
def summary(c: Deps) -> SummaryOut:
    s = c.get_summary.execute()
    return SummaryOut(week=WeekOut(year=s.week.year, iso_week=s.week.iso_week, start=s.week.start, end=s.week.end),
                      total_lines=s.total_lines, within_policy=s.within_policy, open_exceptions=s.open_exceptions,
                      transfers=s.transfers, shadow_mode=s.shadow_mode)
