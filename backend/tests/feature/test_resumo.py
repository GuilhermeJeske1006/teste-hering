"""História: como planejador, abro a mesa e vejo o resumo da semana em modo sombra."""
from fastapi.testclient import TestClient


def test_resumo_mostra_248_linhas_e_7_excecoes_quando_abro_a_mesa(client: TestClient) -> None:
    """Dado o seed da semana 41, quando peço o resumo, então vejo 248 linhas, 7 exceções e modo sombra."""
    body = client.get("/api/summary").json()
    assert body["total_lines"] == 248
    assert body["open_exceptions"] == 7
    assert body["transfers"] == 3
    assert body["shadow_mode"] is True
    assert body["week"] == {"year": 2026, "iso_week": 41, "start": "2026-10-05", "end": "2026-10-11"}


def test_linhas_dentro_da_politica_excluem_as_referenciadas_quando_ha_excecoes(client: TestClient) -> None:
    """Dado que nada foi decidido, quando peço o resumo, então 131 linhas seguem sozinhas."""
    assert client.get("/api/summary").json()["within_policy"] == 131


def test_health_informa_cliente_deterministico_quando_sem_chave(client: TestClient) -> None:
    """Dado que não há ANTHROPIC_API_KEY, quando peço o health, então o LLM ativo é o determinístico."""
    assert client.get("/api/health").json() == {"status": "ok", "llm": "deterministic"}


def test_excecoes_vem_em_ordem_de_severidade_com_a_critica_primeiro_quando_listo(client: TestClient) -> None:
    """Dado a fila da semana, quando listo as exceções, então a crítica vem primeiro e a baixa por último."""
    items = client.get("/api/exceptions").json()
    assert [e["severity"] for e in items] == ["critical", "high", "high", "medium", "medium", "medium", "low"]
    first = items[0]
    assert set(first) >= {"id", "rule", "severity", "title", "recommendation", "explanation", "facts", "status"}
    assert first["status"] == "open" and first["decision"] is None


def test_status_invalido_da_422_quando_filtro_a_fila(client: TestClient) -> None:
    """Dado um filtro inválido, quando listo as exceções, então recebo 422 no formato de erro padrão."""
    res = client.get("/api/exceptions", params={"status": "talvez"})
    assert res.status_code == 422
    assert res.json()["error"]["code"] == "validation_error"
