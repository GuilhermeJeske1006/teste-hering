"""Comportamento específico do adaptador Anthropic: payload, nova tentativa e erro 503."""
import json

import httpx
import pytest

from app.application.errors import LlmUnavailable
from app.application.ports import Message
from app.infrastructure.llm_anthropic import AnthropicLLMClient


def _client(*responses: httpx.Response | Exception, seen: list[httpx.Request] | None = None) -> AnthropicLLMClient:
    queue = list(responses)

    def handler(request: httpx.Request) -> httpx.Response:
        if seen is not None:
            seen.append(request)
        item = queue.pop(0)
        if isinstance(item, Exception):
            raise item
        return item
    return AnthropicLLMClient("k", "modelo-x", transport=httpx.MockTransport(handler))


OK = httpx.Response(200, json={"content": [{"type": "text", "text": "Olá"}]})


def test_envia_sistema_separado_modelo_e_chave_quando_chama_a_api() -> None:
    seen: list[httpx.Request] = []
    out = _client(OK, seen=seen).complete([Message("system", "regras"), Message("user", "oi")], max_tokens=10)
    body = json.loads(seen[0].content)
    assert out == "Olá"
    assert body["system"] == "regras" and body["model"] == "modelo-x" and body["max_tokens"] == 10
    assert body["messages"] == [{"role": "user", "content": "oi"}]
    assert seen[0].headers["x-api-key"] == "k"


def test_tenta_de_novo_uma_vez_quando_rede_falha() -> None:
    assert _client(httpx.ConnectError("caiu"), OK).complete([Message("user", "oi")], max_tokens=10) == "Olá"


def test_tenta_de_novo_quando_servidor_sobrecarregado() -> None:
    assert _client(httpx.Response(529), OK).complete([Message("user", "oi")], max_tokens=10) == "Olá"


def test_lanca_indisponivel_quando_falha_duas_vezes() -> None:
    with pytest.raises(LlmUnavailable):
        _client(httpx.ReadTimeout("lento"), httpx.Response(500)).complete([Message("user", "oi")], max_tokens=10)


def test_lanca_indisponivel_sem_nova_tentativa_quando_chave_invalida() -> None:
    seen: list[httpx.Request] = []
    with pytest.raises(LlmUnavailable):
        _client(httpx.Response(401), OK, seen=seen).complete([Message("user", "oi")], max_tokens=10)
    assert len(seen) == 1
