"""História: como planejador, decido as exceções e tudo fica no registro de auditoria."""
from fastapi.testclient import TestClient

from tests.feature.conftest import open_exceptions

REASON = "Restrição comercial com o franqueado"


def _decide(client: TestClient, exc_id: str, **body: object):  # type: ignore[no-untyped-def]
    return client.post(f"/api/exceptions/{exc_id}/decision", json=body)


def test_aprovar_tira_da_fila_e_grava_no_registro_quando_aprovo(client: TestClient) -> None:
    """Dado uma exceção aberta, quando aprovo, então ela sai das abertas e o registro mostra a aprovação."""
    exc = open_exceptions(client)[0]
    res = _decide(client, exc["id"], action="approve")
    assert res.status_code == 200 and res.json()["status"] == "approved"
    assert exc["id"] not in [e["id"] for e in open_exceptions(client)]
    assert client.get("/api/summary").json()["open_exceptions"] == 6
    log = client.get("/api/audit-log").json()
    assert log[0]["action"] == "approve" and log[0]["subject"] == exc["title"]
    assert set(log[0]) >= {"timestamp", "actor", "action", "subject", "detail"}


def test_rejeitar_sem_motivo_da_422_quando_reason_ausente(client: TestClient) -> None:
    """Dado uma exceção aberta, quando rejeito sem motivo, então recebo 422 reason_required."""
    exc = open_exceptions(client)[0]
    res = _decide(client, exc["id"], action="reject")
    assert res.status_code == 422 and res.json()["error"]["code"] == "reason_required"
    assert client.get("/api/summary").json()["open_exceptions"] == 7


def test_rejeitar_com_motivo_grava_o_motivo_quando_informado(client: TestClient) -> None:
    """Dado uma exceção aberta, quando rejeito com motivo, então o motivo fica na exceção e no registro."""
    exc = open_exceptions(client)[1]
    body = _decide(client, exc["id"], action="reject", reason=REASON).json()
    assert body["status"] == "rejected" and body["decision"]["reason"] == REASON
    assert client.get("/api/audit-log", params={"limit": 1}).json()[0]["detail"] == REASON


def test_decidir_duas_vezes_da_409_quando_ja_decidida(client: TestClient) -> None:
    """Dado uma exceção aprovada, quando tento decidir de novo, então recebo 409 already_decided."""
    exc = open_exceptions(client)[0]
    _decide(client, exc["id"], action="approve")
    res = _decide(client, exc["id"], action="reject", reason=REASON)
    assert res.status_code == 409 and res.json()["error"]["code"] == "already_decided"


def test_desfazer_reabre_a_excecao_e_registra_quando_peco_undo(client: TestClient) -> None:
    """Dado uma exceção rejeitada, quando desfaço, então ela volta para abertas e o undo vai para o registro."""
    exc = open_exceptions(client)[0]
    _decide(client, exc["id"], action="reject", reason=REASON)
    body = _decide(client, exc["id"], action="undo").json()
    assert body["status"] == "open" and body["decision"] is None
    assert client.get("/api/summary").json()["open_exceptions"] == 7
    assert [e["action"] for e in client.get("/api/audit-log", params={"limit": 2}).json()] == ["undo", "reject"]


def test_desfazer_sem_decisao_da_409_quando_excecao_aberta(client: TestClient) -> None:
    """Dado uma exceção aberta, quando peço undo, então recebo 409 not_decided."""
    res = _decide(client, open_exceptions(client)[0]["id"], action="undo")
    assert res.status_code == 409 and res.json()["error"]["code"] == "not_decided"


def test_decidir_excecao_inexistente_da_404_quando_id_desconhecido(client: TestClient) -> None:
    """Dado um id que não existe, quando decido, então recebo 404."""
    res = _decide(client, "naoexiste0", action="approve")
    assert res.status_code == 404 and res.json()["error"]["code"] == "exception_not_found"


def test_acao_invalida_da_422_quando_corpo_errado(client: TestClient) -> None:
    """Dado uma ação fora do contrato, quando decido, então recebo 422 de validação."""
    res = _decide(client, open_exceptions(client)[0]["id"], action="delete")
    assert res.status_code == 422 and res.json()["error"]["code"] == "validation_error"


def test_registro_vem_do_mais_novo_para_o_mais_antigo_quando_listo(client: TestClient) -> None:
    """Dado duas decisões, quando leio o registro, então a mais nova vem primeiro e a recomendação do sistema depois."""
    items = open_exceptions(client)
    _decide(client, items[0]["id"], action="approve")
    _decide(client, items[1]["id"], action="approve")
    log = client.get("/api/audit-log").json()
    assert [e["subject"] for e in log[:2]] == [items[1]["title"], items[0]["title"]]
    assert log[-1]["action"] == "recommend"


def test_filtro_por_status_mostra_aprovadas_quando_pedido(client: TestClient) -> None:
    """Dado uma exceção aprovada, quando filtro por approved, então só ela aparece."""
    exc = open_exceptions(client)[0]
    _decide(client, exc["id"], action="approve")
    approved = client.get("/api/exceptions", params={"status": "approved"}).json()
    assert [e["id"] for e in approved] == [exc["id"]]
