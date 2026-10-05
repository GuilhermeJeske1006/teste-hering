"""Schema pydantic que valida a saída do agente de sinais antes de virar objeto de domínio."""
from __future__ import annotations

import json
from collections.abc import Mapping

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.domain.model import SignalType

MIN_PCT = -100


class AdjustmentPayload(BaseModel):
    """Ajuste percentual pedido pela mensagem."""

    model_config = ConfigDict(extra="ignore")

    scope: str = Field(min_length=1)
    pct: float = Field(ge=MIN_PCT)


class SignalPayload(BaseModel):
    """Formato exigido da resposta do LLM (regras.md §11)."""

    model_config = ConfigDict(extra="ignore")

    store: str | None = None
    type: SignalType
    event: str | None = None
    adjustments: list[AdjustmentPayload] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)
    requires_human: bool = False
    reason: str = ""


class InvalidSignalPayload(ValueError):
    """A resposta do LLM não respeita o schema ou cita loja ou produto inexistente."""


def parse_signal_payload(raw: str, stores: set[str], sizes_by_sku: Mapping[str, tuple[str, ...]]) -> SignalPayload:
    """Extrai o JSON da resposta, valida o schema e confere lojas e escopos contra o catálogo."""
    start, end = raw.find("{"), raw.rfind("}")
    if start < 0 or end <= start:
        raise InvalidSignalPayload("nenhum objeto JSON encontrado")
    try:
        payload = SignalPayload.model_validate(json.loads(raw[start:end + 1]))
    except (json.JSONDecodeError, ValidationError) as err:
        raise InvalidSignalPayload(str(err).splitlines()[0]) from err
    if payload.store is not None and payload.store not in stores:
        raise InvalidSignalPayload(f"loja inexistente: {payload.store}")
    for adj in payload.adjustments:
        if not _valid_scope(adj.scope, sizes_by_sku):
            raise InvalidSignalPayload(f"escopo inválido: {adj.scope}")
    return payload


def _valid_scope(scope: str, sizes_by_sku: Mapping[str, tuple[str, ...]]) -> bool:
    if scope == "all" or scope in sizes_by_sku:
        return True
    sku, _, size = scope.partition(":")
    return size in sizes_by_sku.get(sku, ())
