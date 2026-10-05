"""Caso de uso: agente de sinais transforma mensagem livre em ajuste estruturado (regras.md §11)."""
from __future__ import annotations

from app.application.errors import SignalUnparseable
from app.application.ports import LLMClient, Message, PlanReader
from app.application.prompts import MESSAGE_CLOSE, MESSAGE_OPEN, SIGNAL_RETRY, SIGNAL_SYSTEM, as_data, catalog_lines
from app.application.signal_schema import InvalidSignalPayload, SignalPayload, parse_signal_payload
from app.domain.model import Policies, SignalAdjustment, SignalInterpretation
from app.domain.signals import signal_requires_human

MAX_ATTEMPTS = 2
SIGNAL_MAX_TOKENS = 400


class InterpretSignal:
    """Pede ao LLM a estrutura do sinal, valida por schema e aplica a política no código."""

    def __init__(self, llm: LLMClient, plan: PlanReader) -> None:
        self._llm, self._plan = llm, plan

    def execute(self, text: str, store: str | None = None) -> SignalInterpretation:
        data = self._plan.current().data
        store_ids = {s.id for s in data.stores}
        chosen_store = store if store in store_ids else None
        stores, skus = catalog_lines(data)
        hint = f"\nLoja informada pelo usuário: {chosen_store}" if chosen_store else ""
        messages = [Message("system", SIGNAL_SYSTEM.format(stores=stores, skus=skus)),
                    Message("user", f"{MESSAGE_OPEN}\n{as_data(text)}\n{MESSAGE_CLOSE}{hint}")]
        sizes_by_sku = {k.id: k.sizes for k in data.skus}
        for _ in range(MAX_ATTEMPTS):
            raw = self._llm.complete(messages, max_tokens=SIGNAL_MAX_TOKENS)
            try:
                payload = parse_signal_payload(raw, store_ids, sizes_by_sku)
            except InvalidSignalPayload as err:
                messages = [*messages, Message("assistant", raw), Message("user", SIGNAL_RETRY.format(error=err))]
                continue
            return self._to_domain(payload, chosen_store, data.policies)
        raise SignalUnparseable("Não consegui interpretar a mensagem. Reescreva com mais detalhes e tente de novo.")

    @staticmethod
    def _to_domain(payload: SignalPayload, chosen_store: str | None, policies: Policies) -> SignalInterpretation:
        adjustments = tuple(SignalAdjustment(a.scope, a.pct) for a in payload.adjustments)
        return SignalInterpretation(
            store=chosen_store or payload.store,
            type=payload.type,
            event=payload.event,
            adjustments=adjustments,
            confidence=payload.confidence,
            requires_human=signal_requires_human(payload.type, adjustments, policies),
            reason=payload.reason,
        )
