"""Suíte de contrato do LLMClient (Liskov): todo adaptador passa pelos mesmos testes (ADR 0006)."""
from __future__ import annotations

import json
from collections.abc import Callable

import httpx
import pytest

from app.application.ports import LLMClient, Message
from app.infrastructure.llm_anthropic import AnthropicLLMClient
from app.infrastructure.llm_deterministic import DeterministicLLMClient


def _anthropic_ok() -> AnthropicLLMClient:
    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        echo = body["messages"][-1]["content"][:40]
        return httpx.Response(200, json={"content": [{"type": "text", "text": f"Resposta para: {echo}"}]})
    return AnthropicLLMClient("chave-de-teste", transport=httpx.MockTransport(handler))


ADAPTERS: dict[str, Callable[[], LLMClient]] = {
    "deterministic": DeterministicLLMClient,
    "anthropic": _anthropic_ok,
}


@pytest.fixture(params=list(ADAPTERS), ids=list(ADAPTERS))
def client(request: pytest.FixtureRequest) -> LLMClient:
    return ADAPTERS[request.param]()


def test_devolve_texto_nao_vazio_quando_recebe_pergunta(client: LLMClient) -> None:
    out = client.complete([Message("user", "Olá, tudo bem?")], max_tokens=50)
    assert isinstance(out, str) and out.strip()


def test_aceita_sistema_e_historico_quando_conversa_tem_varios_turnos(client: LLMClient) -> None:
    msgs = [Message("system", "Responda em pt-BR."), Message("user", "Oi"), Message("assistant", "Olá!"),
            Message("user", "Qual é a semana?")]
    assert client.complete(msgs, max_tokens=50).strip()


def test_nao_altera_a_lista_de_mensagens_quando_completa(client: LLMClient) -> None:
    msgs = [Message("user", "Oi")]
    client.complete(msgs, max_tokens=50)
    assert msgs == [Message("user", "Oi")]


def test_rejeita_conversa_vazia_quando_nao_ha_mensagens(client: LLMClient) -> None:
    with pytest.raises(ValueError):
        client.complete([], max_tokens=50)
