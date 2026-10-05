"""Composition root: ÚNICO lugar que instancia adaptadores de infraestrutura (ADR 0003).

A configuração vem só do ambiente: MESA_DB_PATH, MESA_SEED_PATH, ANTHROPIC_API_KEY e ANTHROPIC_MODEL.
"""
from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from app.application.context_builder import ContextBuilder
from app.application.ports import LLMClient
from app.application.use_cases.ask_copilot import AskCopilot
from app.application.use_cases.catalog import ListPolicies, ListSignals, ListSkus, ListStores, ListTransfers
from app.application.use_cases.decide_exception import DecideException
from app.application.use_cases.generate_plan import GeneratePlan
from app.application.use_cases.get_audit_log import GetAuditLog
from app.application.use_cases.get_plan_for_sku import GetPlanForSku
from app.application.use_cases.get_summary import GetSummary
from app.application.use_cases.interpret_signal import InterpretSignal
from app.application.use_cases.list_exceptions import ListExceptions
from app.domain.engine import AllocationEngine
from app.domain.rules import default_rules
from app.infrastructure.clock import SystemClock
from app.infrastructure.llm_anthropic import DEFAULT_MODEL, AnthropicLLMClient
from app.infrastructure.llm_deterministic import DeterministicLLMClient
from app.infrastructure.memory_repos import InMemoryPlanStore
from app.infrastructure.seed_json import JsonSeedSource
from app.infrastructure.sqlite_repos import SqliteAuditLog, SqliteDecisionRepository

APP_DIR = Path(__file__).resolve().parent
DEFAULT_SEED_PATH = APP_DIR / "seed" / "seed.json"
DEFAULT_DB_PATH = APP_DIR.parent / "data" / "mesa.db"


@dataclass(frozen=True, slots=True)
class Container:
    """Casos de uso prontos para os routers, mais o nome do cliente LLM ativo."""

    llm_name: str
    get_summary: GetSummary
    list_exceptions: ListExceptions
    decide_exception: DecideException
    get_plan_for_sku: GetPlanForSku
    list_skus: ListSkus
    list_stores: ListStores
    list_transfers: ListTransfers
    list_signals: ListSignals
    list_policies: ListPolicies
    get_audit_log: GetAuditLog
    interpret_signal: InterpretSignal
    ask_copilot: AskCopilot


def _llm_from_env(env: Mapping[str, str]) -> tuple[LLMClient, str]:
    api_key = env.get("ANTHROPIC_API_KEY", "").strip()
    if api_key:
        return AnthropicLLMClient(api_key, env.get("ANTHROPIC_MODEL") or DEFAULT_MODEL), "anthropic"
    return DeterministicLLMClient(), "deterministic"


def build_container(env: Mapping[str, str] | None = None) -> Container:
    """Monta o grafo de dependências e calcula o plano da semana."""
    env = os.environ if env is None else env
    seed_path = Path(env.get("MESA_SEED_PATH") or DEFAULT_SEED_PATH)
    db_path = Path(env.get("MESA_DB_PATH") or DEFAULT_DB_PATH)
    llm, llm_name = _llm_from_env(env)
    plans, clock = InMemoryPlanStore(), SystemClock()
    decisions, audit = SqliteDecisionRepository(db_path), SqliteAuditLog(db_path)
    GeneratePlan(JsonSeedSource(seed_path), AllocationEngine(default_rules()), plans, audit, clock).execute()
    return Container(
        llm_name=llm_name,
        get_summary=GetSummary(plans, decisions),
        list_exceptions=ListExceptions(plans, decisions),
        decide_exception=DecideException(plans, decisions, decisions, audit, clock),
        get_plan_for_sku=GetPlanForSku(plans),
        list_skus=ListSkus(plans),
        list_stores=ListStores(plans),
        list_transfers=ListTransfers(plans),
        list_signals=ListSignals(plans),
        list_policies=ListPolicies(plans),
        get_audit_log=GetAuditLog(audit),
        interpret_signal=InterpretSignal(llm, plans),
        ask_copilot=AskCopilot(llm, ContextBuilder(plans, decisions)),
    )
