"""História: como planejador, pergunto ao copiloto e ele responde com base nos dados da mesa."""
from fastapi.testclient import TestClient


def test_copiloto_responde_citando_excecao_existente_quando_pergunto_o_que_depende_de_mim(client: TestClient) -> None:
    """Dado a fila da semana, quando pergunto o que depende de mim, então a resposta cita exceções reais."""
    res = client.post("/api/copilot/ask", json={"question": "Quais decisões desta semana dependem de mim?",
                                                "history": []})
    body = res.json()
    ids = {e["id"] for e in client.get("/api/exceptions").json()}
    assert res.status_code == 200 and len(body["answer"]) > 20
    assert body["sources"] and set(body["sources"]) <= ids


def test_copiloto_aceita_historico_e_produto_em_foco_quando_conversa_continua(client: TestClient) -> None:
    """Dado um histórico e o produto em foco, quando pergunto, então recebo uma resposta nova."""
    res = client.post("/api/copilot/ask", json={
        "question": "Por que transferir camiseta de Brusque?", "focus_sku": "CB-PT",
        "history": [{"role": "user", "content": "Oi"}, {"role": "assistant", "content": "Olá!"}]})
    assert res.status_code == 200 and "Brusque" in res.json()["answer"]


def test_pergunta_vazia_da_422_quando_envio(client: TestClient) -> None:
    """Dado uma pergunta vazia, quando envio, então recebo 422."""
    assert client.post("/api/copilot/ask", json={"question": "", "history": []}).status_code == 422
